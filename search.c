#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define CSV_FILE "parcels.csv"
#define MAX_LINE 1024
#define MAX_FIELD 256
#define MAX_RESULTS 1002

static int parse_field(const char *line,int pos, char *out,int out_sz)
{
    int i=0;
    out[0]= '\0';
    if (line[pos] == '"') {
        pos++;                          /* skip opening quote */
        while (line[pos] && i < out_sz - 1) {
            if (line[pos] == '"') {
                if (line[pos + 1] == '"') { /* escaped quote "" */
                    out[i++] = '"';
                    pos += 2;
                } else {
                    pos++;              /* closing quote */
                    break;
                }
            } else {
                out[i++] = line[pos++];
            }
        }
    } else {
        while (line[pos] && line[pos] != ',' && line[pos] != '\n' &&
               line[pos] != '\r' && i < out_sz - 1) {
            out[i++] = line[pos++];
        }
    }
    out[i] = '\0';

    if (line[pos] == ',') pos++;       /* skip comma separator */
    return pos;
}
static int icontains(const char *haystack, const char *needle) {
    if (!needle || needle[0] == '\0') return 1; /* empty matches all */
    char h[MAX_FIELD], n[MAX_FIELD];
    int i;
    for (i = 0; haystack[i] && i < MAX_FIELD - 1; i++)
        h[i] = tolower((unsigned char)haystack[i]);
    h[i] = '\0';
    for (i = 0; needle[i] && i < MAX_FIELD - 1; i++)
        n[i] = tolower((unsigned char)needle[i]);
    n[i] = '\0';
    return strstr(h, n) != NULL;
    }
static int date_in_range(const char *date, const char *from, const char *to)
{
    int ok = 1;
    if (from && from[0]) ok = ok && (strcmp(date, from) >= 0);
    if (to   && to[0])   ok = ok && (strcmp(date, to)   <= 0);
    return ok;
}
static void print_result(
    const char *tracking,
    const char *s_name, const char *s_contact, const char *s_addr, const char *s_city,
    const char *r_name, const char *r_contact, const char *r_addr, const char *r_city,
    const char *weight, const char *type, const char *instructions,
    const char *date,   const char *time_val)
{
    printf("RESULT_START\n");
    printf("Tracking No: %s\n",      tracking);
    printf("Sender: %s | %s | %s | %s\n", s_name, s_contact, s_addr, s_city);
    printf("Receiver: %s | %s | %s | %s\n", r_name, r_contact, r_addr, r_city);
    printf("Weight: %s kg\n",        weight);
    printf("Type: %s\n",             type);
    printf("Instructions: %s\n",     instructions);
    printf("Date: %s\n",             date);
    printf("Time: %s\n",             time_val);
    printf("RESULT_END\n");
}

/* â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
int main(int argc, char *argv[]) {

    if (argc < 2) {
        fprintf(stderr, "Usage: search_parcel <mode> [args...]\n");
        fprintf(stderr, "  Modes: tracking <num>  |  location <city>  |  date <from> <to>  |  location_date <city> <from> <to>\n");
        return 1;
    }

    const char *mode = argv[1];

    /* collect search parameters */
    const char *search_tracking  = NULL;
    const char *search_city      = NULL;
    const char *search_from_date = NULL;
    const char *search_to_date   = NULL;

    if (strcmp(mode, "tracking") == 0) {
        if (argc < 3) { fprintf(stderr, "tracking: need <tracking_number>\n"); return 1; }
        search_tracking = argv[2];

    } else if (strcmp(mode, "location") == 0) {
        if (argc < 3) { fprintf(stderr, "location: need <city>\n"); return 1; }
        search_city = argv[2];

    } else if (strcmp(mode, "date") == 0) {
        if (argc < 4) { fprintf(stderr, "date: need <from_date> <to_date>\n"); return 1; }
        search_from_date = argv[2];
        search_to_date   = argv[3];

    } else if (strcmp(mode, "location_date") == 0) {
        if (argc < 5) { fprintf(stderr, "location_date: need <city> <from_date> <to_date>\n"); return 1; }
        search_city      = argv[2];
        search_from_date = argv[3];
        search_to_date   = argv[4];

    } else {
        fprintf(stderr, "Unknown mode: %s\n", mode);
        return 1;
    }

    /* open CSV */
    FILE *fp = fopen(CSV_FILE, "r");
    if (!fp) {
        fprintf(stderr, "ERROR: Cannot open %s\n", CSV_FILE);
        return 1;
    }

    char line[MAX_LINE];
    int  found = 0;
    int  first_line = 1;
     while (fgets(line, sizeof(line), fp)) {
        /* skip header row */
        if (first_line) { first_line = 0; continue; }

        /* skip blank lines */
        if (line[0] == '\n' || line[0] == '\r') continue;

        char f[14][MAX_FIELD];
        int  pos = 0;
        for (int i = 0; i < 14; i++) {
            pos = parse_field(line, pos, f[i], MAX_FIELD);
        }

        /* f[0]=tracking, f[1]=s_name, f[2]=s_contact, f[3]=s_addr, f[4]=s_city
           f[5]=r_name, f[6]=r_contact, f[7]=r_addr, f[8]=r_city
           f[9]=weight, f[10]=type, f[11]=instructions, f[12]=date, f[13]=time */

        int match = 0;

        if (strcmp(mode, "tracking") == 0) {
            match = (strcasecmp(f[0], search_tracking) == 0);

        } else if (strcmp(mode, "location") == 0) {
            match = icontains(f[4], search_city) || icontains(f[8], search_city);

        } else if (strcmp(mode, "date") == 0) {
            match = date_in_range(f[12], search_from_date, search_to_date);

        } else if (strcmp(mode, "location_date") == 0) {
            match = (icontains(f[4], search_city) || icontains(f[8], search_city))
                    && date_in_range(f[12], search_from_date, search_to_date);
        }

        if (match) {
            print_result(f[0], f[1], f[2], f[3], f[4],
                         f[5], f[6], f[7], f[8],
                         f[9], f[10], f[11], f[12], f[13]);
            found++;
            if (found >= MAX_RESULTS) break;
        }
    }

    fclose(fp);
    printf("TOTAL: %d\n", found);

    if (found == 0)
        printf("NO_RESULTS\n");

    return 0;
}

