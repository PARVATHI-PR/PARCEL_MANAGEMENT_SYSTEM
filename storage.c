#include <stdio.h>
#include <string.h>
#include <time.h>
#include "storage.h"

#define FILE_NAME "parcels.csv"

// Check if file exists
int file_exists(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (f == NULL) return 0;
    fclose(f);
    return 1;
}

// Get current date and time
void get_current_datetime(char *buffer) {
    time_t t;
    struct tm *tm_info;

    time(&t);
    tm_info = localtime(&t);

    strftime(buffer, 50, "%Y-%m-%d %H:%M:%S", tm_info);
}

// Write CSV header
void write_csv_header(FILE *f) {
    fprintf(f,
        "tracking_number,sender_name,sender_contact,sender_address,"
        "receiver_name,receiver_contact,receiver_address,"
        "weight_kg,parcel_type,special_instructions,created_at\n");
}

// Write one parcel row
void write_csv_row(FILE *f, const Parcel *p) {

    // Always set special instructions to "None"
    char special[] = "None";

    fprintf(f,
        "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%.2f,\"%s\",\"%s\",\"%s\"\n",
        p->tracking_number,
        p->sender_name,
        p->sender_contact,
        p->sender_address,
        p->receiver_name,
        p->receiver_contact,
        p->receiver_address,
        p->weight,
        p->parcel_type,
        special,
        p->created_at
    );
}

// Save parcel to CSV
void save_to_csv(Parcel *p) {

    int exists = file_exists(FILE_NAME);

    // Auto date-time
    get_current_datetime(p->created_at);

    FILE *f = fopen(FILE_NAME, "a");
    if (f == NULL) {
        printf("[ERROR] Could not open %s\n", FILE_NAME);
        return;
    }

    // Write header only once
    if (!exists) {
        write_csv_header(f);
    }

    // Write row
    write_csv_row(f, p);

    fclose(f);
}