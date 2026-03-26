#ifndef STORAGE_H
#define STORAGE_H

struct Parcel {
    int trackingID;
    char sender[50];
    char receiver[50];
    char date[20];
    char location[50];
};

// Function declarations
void storeParcel(struct Parcel p);
int getParcelByID(int id, struct Parcel *result);
int getParcelsByLocationAndDate(char loc[], char date[], struct Parcel results[], int maxResults);

#endif