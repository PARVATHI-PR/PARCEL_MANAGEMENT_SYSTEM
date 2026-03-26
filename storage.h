#ifndef STORAGE_H
#define STORAGE_H

#include <stdio.h>   // for FILE

// Define Parcel structure
typedef struct {
    char tracking_number[50];

    char sender_name[100];
    char sender_contact[20];
    char sender_address[200];

    char receiver_name[100];
    char receiver_contact[20];
    char receiver_address[200];

    float weight;
    char parcel_type[50];
    char special_instructions[200]; // still here, but always "None"
    char created_at[50];

} Parcel;

// Function declarations
void save_to_csv(Parcel *p);
void get_current_datetime(char *date, char *time_str); // updated
void write_csv_row(FILE *f, const Parcel *p, const char *date, const char *time_str); // updated

#endif // STORAGE_H