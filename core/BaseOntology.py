from owlready2 import *

DATE_REPRESENTATION = str

# import datetime
# DATE_REPRESENTATION = datetime.datetime

baseOnto = get_ontology("file://wsu_datasets/hh/BaseOntology.owl")

with baseOnto:
    class Sensor(Thing):
        pass

    class BatterySensor(Sensor):
        pass

    class DoorSensor(Sensor):
        pass

    class LightSwitchSensor(Sensor):
        pass

    class LightSensor(Sensor):
        pass

    class MotionSensor(Sensor):
        pass

    class WideAreaMotionSensor(Sensor):
        pass

    class TemperatureSensor(Sensor):
        pass

    class Activity(Thing):
        pass

    class BatheActivity(Activity):
        pass

    class BedToiletTransitionActivity(Activity):
        pass

    class CaregiverActivity(Activity):
        pass

    class CookActivity(Activity):
        pass

    class CookBreakfastActivity(CookActivity):
        pass

    class CookDinnerActivity(CookActivity):
        pass

    class CookLunchActivity(CookActivity):
        pass

    class DressActivity(Activity):
        pass

    class DrinkActivity(Activity):
        pass

    class DrugManagementActivity(Activity):
        pass

    class EatActivity(Activity):
        pass

    class EatBreakfastActivity(EatActivity):
        pass

    class EatDinnerActivity(EatActivity):
        pass

    class EatLunchActivity(EatActivity):
        pass

    class EnterHomeActivity(Activity):
        pass

    class EntertainGuestsActivity(Activity):
        pass

    class TakeMedsActivity(Activity):
        pass

    class TakeEveningMedsActivity(TakeMedsActivity):
        pass

    class TakeMorningMedsActivity(TakeMedsActivity):
        pass

    class ExerciseActivity(Activity):
        pass

    class HousekeepingActivity(Activity):
        pass

    class GroceriesActivity(Activity):
        pass

    class GroomActivity(Activity):
        pass

    class LaundryActivity(Activity):
        pass

    class LeaveHomeActivity(Activity):
        pass

    class MakeBedActivity(Activity):
        pass

    class ParamedicsActivity(Activity):
        pass

    class PersonalHygieneActivity(Activity):
        pass

    class PhoneActivity(Activity):
        pass

    class PianoActivity(Activity):
        pass

    class DishesActivity(Activity):
        pass

    class RelaxActivity(Activity):
        pass

    class SleepActivity(Activity):
        pass

    class ToiletActivity(Activity):
        pass

    class ReadActivity(Activity):
        pass

    class SleepOutOfBedActivity(Activity):
        pass

    class StepOutActivity(Activity):
        pass

    class TakeMedicineActivity(Activity):
        pass

    class WashDishesActivity(Activity):
        pass

    class WashLunchDishesActivity(WashDishesActivity):
        pass

    class WashBreakfastDishesActivity(WashDishesActivity):
        pass

    class WashDinnerDishesActivity(WashDishesActivity):
        pass

    class WatchTVActivity(Activity):
        pass

    class WorkActivity(Activity):
        pass

    class WorkAtDeskActivity(WorkActivity):
        pass

    class WorkAtTableActivity(WorkActivity):
        pass

    class WorkOnComputerActivity(WorkActivity):
        pass

    class Device(Thing):
        pass

    class Location(Thing):
        pass

    class KitchenLocation(Location):
        pass

    class LivingRoomLocation(Location):
        pass

    class BathroomLocation(Location):
        pass

    class BedroomLocation(Location):
        pass

    class EntranceLocation(Location):
        pass

    class Measure(Thing):
        pass

    class Property(Thing):
        pass

    class hasLocation(Device >> Location, FunctionalProperty):
        python_name = "has_location"

    class isAdjacentTo(Location >> Location):
        python_name = "is_adjacent_to"

    class isEmbeddedBy(Sensor >> Device, FunctionalProperty):
        pass

    class embeds(Device >> Sensor, InverseFunctionalProperty):
        python_name = "embeds"
        inverse_property = isEmbeddedBy

    class isMeasuredBy(Measure >> Sensor, FunctionalProperty):
        python_name = "is_measured_by"

    class hasTimeStamp(DataProperty, FunctionalProperty):
        python_name = 'timestamp'
        domain = [Measure, Activity]
        range = [DATE_REPRESENTATION]

    class hasValue(Measure >> float, FunctionalProperty):
        python_name = 'value'

    class beginsAt(Activity >> DATE_REPRESENTATION, FunctionalProperty):
        python_name = 'begins_at'

    class endsAt(Activity >> DATE_REPRESENTATION, FunctionalProperty):
        python_name = 'ends_at'

    class takesPlaceIn(Activity >> Location):
        pass

    class hasProperty(Location >> Property):
        pass

    class actsOn(Activity >> Property):
        pass

SENSOR_TYPE_TRANSLATION = {
    'BA': BatterySensor,
    'D': DoorSensor,
    'L': LightSwitchSensor,
    'LL': LightSwitchSensor,
    'LS': LightSensor,
    'M': MotionSensor,
    'MA': WideAreaMotionSensor,
    'T': TemperatureSensor
}

LOCATION_TYPE_TRANSLATION = {
    'kitchen': KitchenLocation,
    'living_room': LivingRoomLocation,
    'bedroom': BedroomLocation,
    'bathroom': BathroomLocation,
    'entrance': EntranceLocation
}

ACTIVITY_EVENT = {
    'begin': beginsAt,
    'end': endsAt,
    None: hasTimeStamp
}


ACTIVITY_TYPE_TRANSLATION = {
    "Bathe": BatheActivity,
    "Bed_Toilet_Transition": BedToiletTransitionActivity,
    "Caregiver": CaregiverActivity,
    "Cook": CookActivity,
    "Cook_Breakfast": CookBreakfastActivity,
    "Cook_Dinner": CookDinnerActivity,
    "Cook_Lunch": CookLunchActivity,
    "Dress": DressActivity,
    "Drink": DrinkActivity,
    "Drug_Management": DrugManagementActivity,
    "Eat": EatActivity,
    "Eat_Breakfast": EatBreakfastActivity,
    "Eat_Dinner": EatDinnerActivity,
    "Eat_Lunch": EatLunchActivity,
    "Enter_Home": EnterHomeActivity,
    "Entertain_Guests": EntertainGuestsActivity,
    "Evening_Meds": TakeEveningMedsActivity,
    "Exercise": ExerciseActivity,
    "Housekeeping": HousekeepingActivity,
    "Groceries": GroceriesActivity,
    "Groom": GroomActivity,
    "Laundry": LaundryActivity,
    "Leave_Home": LeaveHomeActivity,
    "Make_Bed": MakeBedActivity,
    "Morning_Meds": TakeMorningMedsActivity,
    "Paramedics": ParamedicsActivity,
    "Personal_Hygiene": PersonalHygieneActivity,
    "Phone": PhoneActivity,
    "Piano": PianoActivity,
    "Cook_Breakfast": CookBreakfastActivity,
    "Dishes": WashDishesActivity,  # CHANGED
    "Dress": DressActivity,
    "Groom": GroomActivity,
    "Relax": RelaxActivity,
    "Sleep": SleepActivity,
    "Toilet": ToiletActivity,
    "Work": WorkActivity,
    "Read": ReadActivity,
    "Relax": RelaxActivity,
    "Sleep": SleepActivity,
    "Sleep_Out_Of_Bed": SleepOutOfBedActivity,
    "Step_Out": StepOutActivity,
    "Take_Medicine": TakeMedsActivity,
    "Toilet": ToiletActivity,
    "Wash_Breakfast_Dishes": WashBreakfastDishesActivity,
    "Wash_Dinner_Dishes": WashDinnerDishesActivity,
    "Wash_Dishes": WashDishesActivity,
    "Wash_Lunch_Dishes": WashLunchDishesActivity,
    "Watch_TV": WatchTVActivity,  # CHANGED
    "Work": WorkActivity,
    "Work_At_Desk": WorkAtDeskActivity,
    "Work_At_Table": WorkAtTableActivity,
    "Work_On_Computer": WorkOnComputerActivity,
}

MEASURE_TYPE_TRANSLATION = {
    'open': True,
    'close': False,
    'on': True,
    'off': False
}

ROOMS_DESCRIPTION = {  # To discover / self organization ?
}
