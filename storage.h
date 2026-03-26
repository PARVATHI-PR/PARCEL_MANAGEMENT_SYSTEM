#ifndef STORAGE_H
#define STORAGE_H

struct Parcel {
    int trackingID;
    char senderName[50];
    char senderAddress[100];
    char receiverName[50];
    char receiverAddress[100];
    char contact[15];
    char status[20];
    char location[50];
    char date[15];
};


void storeParcel(struct Parcel p);

int getParcelByID(int id, struct Parcel *result);

int getParcelsByLocationAndDate(char loc[], char date[], struct Parcel results[], int maxResults);

#endif