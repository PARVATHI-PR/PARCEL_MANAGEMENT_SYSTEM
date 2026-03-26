#include <stdio.h>
#include "details.h"
#include "tracking.h"
 
int main() {
    Person sender, receiver;
    ParcelInfo parcel;
    char tracking_number[30];
 
    printf("\n==============================\n");
    printf("    PARCEL BOOKING SYSTEM     \n");
    printf("==============================\n");
 
    input_person(&sender, "Sender");
    input_person(&receiver, "Receiver");
    input_parcel_info(&parcel);
 
    generate_tracking_number(tracking_number);
 
    printf("\n==============================\n");
    printf("       BOOKING CONFIRMED      \n");
    printf("==============================\n");
    printf("  Tracking No : %s\n", tracking_number);
    printf("  Sender      : %s\n", sender.name);
    printf("  Receiver    : %s\n", receiver.name);
    printf("  Weight      : %.2f kg\n", parcel.weight);
    printf("  Type        : %s\n", parcel.type);
    printf("==============================\n\n");
 
    return 0;
}