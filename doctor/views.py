from django.conf import settings
from django.db import transaction
from doctor.models import (  # Doctor Models
    Users,
    Patients,
    Appointments,
    Consultation,
    NotePad,
    Availability,
    Transactions,
    Doctors,
)
from doctor.serializers import (  # Doctor Serializers
    AppointmentsSerializer,
    PatientsSerializer,
    Patients,
    Doctors,
    AvailabilitySerializer,
    ConsultationSerializer,
    DoctorSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from utilities.utils import (  # Utils
    is_valid_date,
    is_valid_email,
    is_valid_phone,
    get_room_no,
)
from core.decorators import token_required
from core.mixins import DoctorViewMixin
from rest_framework.decorators import api_view
from administrator.models import UserPushNotification
from datetime import ( # Datetime
    datetime,
)
from django.db.models import (
    F,
    Q,
)


@token_required
@api_view(["GET"])
def time_slots(request):
    date = request.GET.get("date")
    if not date:
        return Response(
            {"status": False, "message": "required fields are missing"}, 400
        )
    if not is_valid_date(date, "%Y-%m-%d"):
        return Response(
            {"status": False, "message": "Invalid date format. Please use '%Y-%m-%d'."}
        )

    parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

    today = datetime.today().date()
    if not parsed_date >= today:
        return Response(
            {"status": False, "message": "The provided date is not valid."}, 400
        )

    current_date_time = datetime.now()

    if parsed_date == current_date_time.date():
        avail = (
            Availability.objects.filter(
                date=parsed_date,
                is_booked=False,
                time_slot__start_time__gt=current_date_time.time(),
            )
            .distinct()
            .order_by("time_slot__start_time")
            .annotate(slot_time=F("time_slot__start_time"))
            .values("slot_time")
        )
    else:
        avail = (
            Availability.objects.filter(date=parsed_date, is_booked=False)
            .distinct()
            .order_by("time_slot__start_time")
            .annotate(slot_time=F("time_slot__start_time"))
            .values("slot_time")
        )

    return Response({"status": True, "data": avail})


@token_required
@api_view(["POST"])
def schedule_meeting(request):
    if request.method == "POST":
        data = request.data

        user_required_fields = [
            "id",
            "first_name",
            # "last_name",
            "email",
            "phone_number",
        ]
        patient_required_fields = [
            "name",
            "phone",
            "email",
            "dob",
            "gender",
            "paid_amount",
            "pay_mode",
            "schedule_date",
        ]
        required = False
        message = ""

        if not all(data["user"].get(field) for field in user_required_fields):
            required = True
            message = "Required fields are missing in 'User'."

        if not all(data["patient"].get(field) for field in patient_required_fields):
            required = True
            message = "Required fields are missing in 'patient'."

        if required:
            return Response({"status": False, "message": message}, 400)

        # Extract user data
        user_id = data["user"].get("id")
        user_first_name = data["user"].get("first_name")
        user_last_name = data["user"].get("last_name")
        user_email = data["user"].get("email")
        user_phone_number = data["user"].get("phone_number")

        # Extract patient data
        patient_name = data["patient"].get("name")
        patient_phone = data["patient"].get("phone")
        patient_email = data["patient"].get("email")
        patient_dob = data["patient"].get("dob")
        patient_gender = data["patient"].get("gender")
        patient_paid_amount = data["patient"].get("paid_amount")
        patient_pay_mode = data["patient"].get("pay_mode")
        patient_schedule_date = data["patient"].get("schedule_date")
        pre_health_issue = data["patient"].get("pre_health_issue", "").lower() == "yes"
        pre_health_issue_text = data["patient"].get("pre_health_issue_text")
        treatment_undergoing = (
            data["patient"].get("treatment_undergoing", "").lower() == "yes"
        )
        treatment_undergoing_text = data["patient"].get("treatment_undergoing_text")
        treatment_allergies = (
            data["patient"].get("treatment_allergies", "").lower() == "yes"
        )
        treatment_allergies_text = data["patient"].get("treatment_allergies_text")
        additional_note = data["patient"].get("additional_note")

        if not is_valid_email(patient_email):
            return Response(
                {
                    "status": False,
                    "message": "Invalid email address format. Please provide a valid email address.",
                },
                400,
            )

        if not is_valid_phone(patient_phone):
            return Response(
                {
                    "status": False,
                    "message": "Invalid phone number. Please provide a valid phone number.",
                },
                400,
            )

        if not is_valid_date(patient_schedule_date, "%Y-%m-%d %H:%M"):
            return Response(
                {
                    "status": False,
                    "message": "Invalid schedule date format. Please use YYYY-MM-DD HH:MM.",
                },
                400,
            )

        if not is_valid_date(patient_dob, "%Y-%m-%d"):
            return Response(
                {
                    "status": False,
                    "message": "Invalid DOB date format. Please use YYYY-MM-DD.",
                },
                400,
            )

        try:
            patient_paid_amount = float(patient_paid_amount)
        except:
            # if not isinstance(patient_paid_amount, int or float):
            return Response(
                {
                    "status": False,
                    "message": "Invalid paid amount. Please provide a valid paid amount",
                },
                400,
            )

        try:
            with transaction.atomic():
                users_obj, _ = Users.objects.get_or_create(user_id=user_id)

                users_obj.first_name = user_first_name
                users_obj.last_name = user_last_name
                users_obj.email = user_email
                users_obj.phone_number = user_phone_number
                users_obj.save()

                patient_obj, _ = Patients.objects.get_or_create(
                    user=users_obj,
                    name=patient_name,
                    dob=patient_dob,
                    gender=patient_gender,
                )
                patient_obj.phone=patient_phone
                patient_obj.email=patient_email

                patient_obj.pre_health_issue=pre_health_issue
                patient_obj.pre_health_issue_text=pre_health_issue_text
                patient_obj.treatment_undergoing=treatment_undergoing
                patient_obj.treatment_undergoing_text=treatment_undergoing_text
                patient_obj.treatment_allergies=treatment_allergies
                patient_obj.treatment_allergies_text=treatment_allergies_text
                patient_obj.additional_note=additional_note

                patient_obj.save()

                schedule_date_obj = datetime.strptime(
                    patient_schedule_date, "%Y-%m-%d %H:%M"
                )

                availability_obj = (
                    Availability.objects.select_for_update()
                    .filter(
                        date=schedule_date_obj.date(),
                        time_slot__start_time=schedule_date_obj.time().strftime(
                            "%H:%M"
                        ),
                        is_booked=False,
                    )
                    .order_by("doctor__priority")
                    .first()
                )

                if not availability_obj:
                    return Response(
                        {
                            "status": False,
                            "message": "We couldn't find any available doctors. Please make another selection.",
                        },
                        400,
                    )

                Transactions.objects.create(
                    patient = patient_obj,
                    doctor=availability_obj.doctor,
                    paid_amount=patient_paid_amount,
                    pay_mode=patient_pay_mode,
                )

                appointment_obj = Appointments.objects.create(
                    patient=patient_obj,
                    doctor=availability_obj.doctor,
                    schedule_date=schedule_date_obj,
                    slot_key=availability_obj.id,
                    room_name=get_room_no(),
                    no_cost_consult=settings.NO_COST_CONSULT,
                    meeting_link="http://0.0.0.0:9000/backend/accounts/user/",
                )
                availability_obj.is_booked = True
                availability_obj.save()

                data = {
                    "appointment_id": appointment_obj.appointment_id,
                    "patient": appointment_obj.patient.patient_id,
                    "doctor": appointment_obj.doctor.user.id,
                    "schedule_date": appointment_obj.schedule_date,
                    "slot_key": appointment_obj.slot_key,
                    "room_name": appointment_obj.room_name,
                    "no_cost_consult": appointment_obj.no_cost_consult,
                    "status": appointment_obj.status,
                    "is_attended": appointment_obj.is_attended,
                    "meeting_link": appointment_obj.meeting_link,
                }

                return Response(
                    {
                        "status": True,
                        "message": "The appointment has been successfully created",
                        "data": data,
                    },
                    201,
                )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. Please try again later.",
                    "error": str(e),
                },
                400,
            )


@token_required
@api_view(["PATCH"])
def reschedule_meeting(request):
    if request.method == "PATCH":
        date = request.data.get("date")
        time = request.data.get("time")
        appointment_id = request.data.get("appointment_id")

        if not all([date, time, appointment_id]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        datetime_str = date + " " + time
        input_format = "%Y-%m-%d %H:%M"
        schedule_date_obj = datetime.strptime(datetime_str, input_format)
        try:
            with transaction.atomic():
                availability_obj = (
                    Availability.objects.select_for_update()
                    .filter(
                        date=schedule_date_obj.date(),
                        time_slot__start_time=schedule_date_obj.time(),
                        is_booked=False,
                    )
                    .order_by("doctor__priority")
                    .first()
                )

                if not availability_obj:
                    return Response(
                        {
                            "status": False,
                            "message": "We couldn't find any available doctors. Please make another selection.",
                        },
                        400,
                    )
                try:
                    appointment_obj = Appointments.objects.get(pk=appointment_id)
                except:
                    return Response(
                        {"status": False, "message": "Appointment not found"}, 404
                    )

                # Release preassigned doctor
                avail_dr = Availability.objects.filter(
                    doctor=appointment_obj.doctor, id=appointment_obj.slot_key
                ).first()
                avail_dr.is_booked = False
                avail_dr.save()

                appointment_obj.doctor = availability_obj.doctor
                appointment_obj.schedule_date = schedule_date_obj
                appointment_obj.slot_key = availability_obj.id
                appointment_obj.status = "rescheduled"
                appointment_obj.save()

                availability_obj.is_booked = True
                availability_obj.save()

                return Response(
                    {
                        "status": True,
                        "message": "Appointment has been successfully rescheduled",
                    },
                    200,
                )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. Please try again later",
                },
                400,
            )


@token_required
@api_view(["PATCH"])
def cancel_meeting(request):
    if request.method == "PATCH":
        appointment_id = request.data.get("appointment_id")
        if not appointment_id:
            return Response(
                {"status": False, "message": "Appointment id required"}, 400
            )

        try:
            appointment_obj = Appointments.objects.get(pk=appointment_id)
        except:
            return Response({"status": False, "message": "Appointment not found"}, 404)

        appointment_obj.status = "cancelled"
        appointment_obj.save()
        # Release assigned doctor
        avail_dr = Availability.objects.filter(
            doctor=appointment_obj.doctor, id=appointment_obj.slot_key
        ).first()
        avail_dr.is_booked = False
        avail_dr.save()

        return Response(
            {
                "status": True,
                "message": "Appointment has been successfully cancelled",
            },
            200,
        )


class AppointmentView(DoctorViewMixin):
    def get(self, request):
        search_query = (request.GET.get("search_query", "")).lower()
        list_of_available_search_query = ["pending", "completed", "rescheduled"]
        filter_by_date = request.GET.get("date")
        Appointments_obj = Appointments.objects.filter(doctor__user=request.user)

        if search_query:
            if search_query not in list_of_available_search_query:
                return Response(
                    {
                        "status": False,
                        "message": f"Invalid status provided. Please use one of the following: {', '.join(list_of_available_search_query)}",
                    }
                )
            query_set = Appointments_obj.filter(status=search_query)

        elif filter_by_date:
            if not is_valid_date(filter_by_date, "%Y-%m-%d"):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid schedule date format. Please use YYYY-MM-DD",
                    },
                    400,
                )
            query_set = Appointments_obj.filter(schedule_date__date=filter_by_date)

        else:
            query_set = Appointments_obj

        data = AppointmentsSerializer(
            query_set,
            many=True,
            fields=["patient", "schedule_date", "status", "filter_by"],
        ).data

        display_data = {
            "number_of_appointments": Appointments_obj.count(),
            "unanswered_patient": Appointments_obj.filter(
                status="unanswered_patient"
            ).count(),
        }
        return Response(
            {"status": True, "data": data, "display_data": display_data}, 200
        )


class PatientView(DoctorViewMixin):
    def get(self, request):
        patient_id = request.GET.get("patient_id")
        if patient_id:
            patients = Appointments.objects.filter(
                doctor__user=request.user, patient__patient_id=patient_id
            ).select_related("patient")
        else:
            patients = Appointments.objects.filter(
                doctor__user=request.user
            ).select_related("patient")
        data = AppointmentsSerializer(patients, many=True, fields=["patient"]).data
        return Response({"status": True, "data": data}, 200)


class PatientDetailView(DoctorViewMixin):
    def get(self, request):
        user_id = request.GET.get("user_id")
        name = request.GET.get("name")
        dob = request.GET.get("dob")
        gender = request.GET.get("gender")

        if not all([user_id, name, dob, gender]):
            return Response(
                {"status": False, "message": "required fields are missing"}, 400
            )

        consultation_obj = Consultation.objects.filter(
            Q(appointment__patient__user__user_id=user_id)
            & Q(appointment__doctor__user=request.user)
            & Q(appointment__patient__name=name)
            & Q(appointment__patient__dob=dob)
            & Q(appointment__patient__gender=gender)
        )

        consultation_data = ConsultationSerializer(consultation_obj, many=True).data
        return Response({"status": True, "data": consultation_data}, 200)


class ProfileView(DoctorViewMixin):
    def get(self, request):
        try:
            doctor_obj = Doctors.objects.get(user=request.user)
        except:
            return Response({"status": False, "message": "Doctor not found"})

        data = DoctorSerializer(doctor_obj).data
        return Response({"status": True, "data": data})


class NotificationsView(DoctorViewMixin):
    def get(self, request):
        notifications = UserPushNotification.objects.filter(
            user=request.user
        ).select_related("notification")
        push_notification = []
        for notification in notifications:
            push_notification.append(
                {
                    "id": notification.id,
                    "title": notification.notification.title,
                    "message": notification.notification.message,
                    "created": notification.notification.created,
                    "is_read": notification.is_read,
                }
            )
        return Response({"status": True, "notifications": push_notification}, 200)

    def put(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"status": False, "message": "id not found"}, 400)

        try:
            dr_notification = UserPushNotification.objects.get(id=id)
        except:
            return Response({"status": False, "message": "Notification not found"}, 404)
        dr_notification.is_read = True
        dr_notification.save()
        data = [
            {
                "id": dr_notification.id,
                "title": dr_notification.notification.title,
                "message": dr_notification.notification.message,
                "created": dr_notification.notification.created,
                "is_read": dr_notification.is_read,
            }
        ]
        return Response({"status": True, "notifications": data})


class ConsultView(DoctorViewMixin):
    def post(self, request):
        notepad = request.data.get("notepad")
        room_name = request.data.get("room_name")
        if not all([notepad, room_name]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )
        try:
            appointment_obj = Appointments.objects.get(room_name=room_name)
        except:
            return Response({"status": False, "message": "Room not found"}, 404)

        try:
            # NotePad.objects.create(room_name=room_name, notepad=notepad)
            Consultation.objects.create(
                prescription=notepad,
                appointment=appointment_obj,
            )
            return Response(
                {"status": True, "message": "Your submission was successful"}
            )
        except Exception as e:
            return Response({"status": False, "message": str(e)}, 400)


class AppointmentViewTest(APIView):
    def post(self, request):
        pass


@token_required
@api_view(["GET"])
def my_appointments(request):
    id = request.GET.get("id")
    if not id:
        return Response(
            {"status": False, "message": "Required fields are missing"}, 400
        )

    appointment_obj = Appointments.objects.filter(patient__user__user_id=id)
    data = AppointmentsSerializer(appointment_obj, many=True).data
    return Response({"status": True, "data": data}, 200)
