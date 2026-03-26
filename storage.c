#include <stdio.h>
#include <string.h>
#define FILE_NAME "parcels.txt"
#include "storage.h"

int file_exists(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return 0;
    fclose(f);
    return 1;
}
 
void write_csv_header(FILE *f) {
    fprintf(f,
        "tracking_number,sender_name,sender_contact,sender_address,"
        "receiver_name,receiver_contact,receiver_address,"
        "weight_kg,parcel_type,special_instructions,created_at\n");
}
 
void write_csv_row(FILE *f, const Parcel *p) {
    fprintf(f, "%s,%s,%s,\"%s\",%s,%s,\"%s\",%.2f,%s,\"%s\",%s\n",
        p->tracking_number,
        p->sender_name,    p->sender_contact, p->sender_address,
        p->receiver_name,  p->receiver_contact, p->receiver_address,
        p->weight,         p->parcel_type,
        p->special_instructions, p->created_at);
}
 
void save_to_csv(const Parcel *p) {
    int exists = file_exists(FILE_NAME);
    FILE *f = fopen(FILE_NAME, "a");
    if (!f) { printf("  [ERROR] Could not open %s\n", FILE_NAME); return; }
    if (!exists) write_csv_header(f);
    write_csv_row(f, p);
    fclose(f);
}