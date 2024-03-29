import sys

if __name__ == "__main__":
    from project_setup import *
from doctor.models import DoctorAvailability, DoctorLeave, TimeSlot, Availability
from datetime import datetime
from django.utils import timezone

DATE_FORMATE = "%Y/%m/%d"


def UpdateSlot(day=7):
    day = (timezone.now() + timezone.timedelta(days=day)).strftime(DATE_FORMATE)
    date_obj = datetime.strptime(day, DATE_FORMATE)
    doctors_on_leave = DoctorLeave.objects.filter(
        leave_date=date_obj, is_sanction=True
    ).values_list("doctor__user__id", flat=True)
    day_name = date_obj.strftime("%A")
    doctors = (
        DoctorAvailability.objects.filter(working_days__contains=[day_name])
        .select_related("doctor")
        .exclude(doctor__user__id__in=doctors_on_leave)
    )

    for doctor in doctors:
        slots = TimeSlot.objects.filter(
            start_time__range=(doctor.start_working_hr, doctor.end_working_hr)
        )
        for slot in slots:
            try:
                Availability.objects.create(
                    doctor=doctor.doctor, date=date_obj.date(), time_slot=slot
                )
            except:
                pass
    return date_obj.strftime(DATE_FORMATE)


def DeleteSlot():
    Availability.objects.filter(date__lt=timezone.now().date()).delete()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            argument_value = int(sys.argv[1])
            UpdateSlot(argument_value)
        except:
            print("The argument should be an integer.")
    else:
        UpdateSlot()
    DeleteSlot()
