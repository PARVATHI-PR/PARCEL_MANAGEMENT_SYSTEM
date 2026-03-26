#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "details.h"
#include "tracking.h"
#include "storage.h"

int main() {
    Person sender, receiver;
    ParcelInfo parcel;
    char tracking_number[30];
    Parcel p;   // ✅ Correct

    printf("\n==============================\n");
    printf("    PARCEL BOOKING SYSTEM     \n");
    printf("==============================\n");

    input_person(&sender, "Sender");
    input_person(&receiver, "Receiver");
    input_parcel_info(&parcel);

    generate_tracking_number(tracking_number);

    // ✅ Fill struct correctly
    strncpy(p.tracking_number, tracking_number, sizeof(p.tracking_number) - 1);

    strncpy(p.sender_name, sender.name, sizeof(p.sender_name) - 1);
    strncpy(p.sender_contact, sender.phone, sizeof(p.sender_contact) - 1);
    strncpy(p.sender_address, sender.address, sizeof(p.sender_address) - 1);

    strncpy(p.receiver_name, receiver.name, sizeof(p.receiver_name) - 1);
    strncpy(p.receiver_contact, receiver.phone, sizeof(p.receiver_contact) - 1);
    strncpy(p.receiver_address, receiver.address, sizeof(p.receiver_address) - 1);

    p.weight = parcel.weight;
    strncpy(p.parcel_type, parcel.type, sizeof(p.parcel_type) - 1);

    strncpy(p.special_instructions, "None", sizeof(p.special_instructions) - 1);
    strncpy(p.created_at, tracking_number, sizeof(p.created_at) - 1);

    // ✅ Correct function
    save_to_csv(&p);

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