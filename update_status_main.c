#include <stdio.h>
#include <string.h>
#include "status_update.h"

int main() {
    char tracking[50], status[20], staff_id[50],
         staff_name[100], location[100];

    if (fgets(tracking,   sizeof(tracking),   stdin)) tracking[strcspn(tracking,     "\n")] = 0;
    if (fgets(status,     sizeof(status),     stdin)) status[strcspn(status,         "\n")] = 0;
    if (fgets(staff_id,   sizeof(staff_id),   stdin)) staff_id[strcspn(staff_id,     "\n")] = 0;
    if (fgets(staff_name, sizeof(staff_name), stdin)) staff_name[strcspn(staff_name, "\n")] = 0;
    if (fgets(location,   sizeof(location),   stdin)) location[strcspn(location,     "\n")] = 0;

    if (!is_valid_status(status)) {
        printf("STATUS_ERROR: Invalid status '%s'\n", status);
        printf("Valid: Booked, InTransit, Reached, Delivered\n");
        return 1;
    }

    int ok = save_status_to_csv(tracking, status, staff_id, staff_name, location);
    if (ok) {
        char date[20], time_str[20];
        get_current_datetime_status(date, time_str);
        printf("STATUS_OK\n");
        printf("Tracking No : %s\n", tracking);
        printf("New Status  : %s\n", status);
        printf("Staff       : %s (%s)\n", staff_name, staff_id);
        printf("Location    : %s\n", location);
        printf("Date & Time : %s %s\n", date, time_str);
    } else {
        printf("STATUS_ERROR: Could not save to file\n");
        return 1;
    }
    return 0;
}