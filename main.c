#include <stdio.h>
#include <string.h>
#include "details.h"
#include "tracking.h"
#include "storage.h"

int main() {
    Person sender, receiver;
    ParcelInfo parcel;
    char tracking_number[30];
    struct Parcel p;

    printf("\n==============================\n");
    printf("    PARCEL BOOKING SYSTEM     \n");
    printf("==============================\n");

    input_person(&sender, "Sender");
    input_person(&receiver, "Receiver");
    input_parcel_info(&parcel);

    generate_tracking_number(tracking_number);

    p.trackingID = atoi(tracking_number + 4);
    strncpy(p.senderName,     sender.name,      sizeof(p.senderName)     - 1);
    strncpy(p.senderAddress,  sender.address,   sizeof(p.senderAddress)  - 1);
    strncpy(p.receiverName,   receiver.name,    sizeof(p.receiverName)   - 1);
    strncpy(p.receiverAddress,receiver.address, sizeof(p.receiverAddress)- 1);
    strncpy(p.contact,        sender.phone,     sizeof(p.contact)        - 1);
    strncpy(p.status,         "Booked",         sizeof(p.status)         - 1);
    strncpy(p.location,       "Origin",         sizeof(p.location)       - 1);
    strncpy(p.date,           tracking_number + 4, sizeof(p.date)        - 1);

    storeParcel(p);

    printf("\n==============================\n");
    printf("       BOOKING CONFIRMED      \n");
    printf("==============================\n");
    printf("  Tracking No : %s\n", tracking_number);
    printf("  Sender      : %s\n", sender.name);
    printf("  Receiver    : %s\n", receiver.name);
    printf("  Weight      : %.2f kg\n", parcel.weight);
    printf("  Type        : %s\n", parcel.type);
    printf("  Saved to    : parcels.txt\n");
    printf("==============================\n\n");

    return 0;
}