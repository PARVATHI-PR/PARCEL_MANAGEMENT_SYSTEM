#include <stdio.h>
#include <string.h>
#define FILE_NAME "parcels.txt"
#include "storage.h"


struct Parcel
 {
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


void storeParcel(struct Parcel p) 
{
    FILE *fp = fopen(FILE_NAME, "a");

    if (fp == NULL)
     {
        printf("Error opening file!\n");
        return;
    }

    int written = fprintf(fp, "%d,%s,%s,%s,%s,%s,%s,%s,%s\n",
        p.trackingID,
        p.senderName,
        p.senderAddress,
        p.receiverName,
        p.receiverAddress,
        p.contact,
        p.status,
        p.location,
        p.date
    );

    if (written < 0) 
    {
        printf("Error writing data!\n");
    }

    fclose(fp);
}


int getParcelByID(int id, struct Parcel *result)
 {
    FILE *fp = fopen(FILE_NAME, "r");

    if (fp == NULL)
     {
        return 0;
    }

    struct Parcel p;

    while (fscanf(fp, "%d,%49[^,],%99[^,],%49[^,],%99[^,],%14[^,],%19[^,],%49[^,],%14[^\n]\n",
        &p.trackingID,
        p.senderName,
        p.senderAddress,
        p.receiverName,
        p.receiverAddress,
        p.contact,
        p.status,
        p.location,
        p.date) != EOF) 
        {

        if (p.trackingID == id) 
        {
            *result = p; 
            fclose(fp);
            return 1;
        }
    }

    fclose(fp);
    return 0;
}


int getParcelsByLocationAndDate(char loc[], char date[], struct Parcel results[], int maxResults) 
{
    FILE *fp = fopen(FILE_NAME, "r");

    if (fp == NULL)
     {
        return 0;
    }

    struct Parcel p;
    int count = 0;

    while (fscanf(fp, "%d,%49[^,],%99[^,],%49[^,],%99[^,],%14[^,],%19[^,],%49[^,],%14[^\n]\n",
        &p.trackingID,
        p.senderName,
        p.senderAddress,
        p.receiverName,
        p.receiverAddress,
        p.contact,
        p.status,
        p.location,
        p.date) != EOF) 
        {
        if (strcmp(p.location, loc) == 0 && strcmp(p.date, date) == 0)
         {
            if (count < maxResults) 
            {
                results[count++] = p;
            }
        }
    }
    fclose(fp);
    return count;
}