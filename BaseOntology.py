import datetime
from owlready2 import *

DATE_REPRESENTATION = str
# DATE_REPRESENTATION = datetime.datetime

onto = get_ontology("file:///home/yop/Programmation/Recherche/wsu_datasets/ontology/hh101.owl")

with onto : 
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

	class BathActivity(Activity):
		pass

	class BedToiletTransitionActivity(Activity): 
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

	class GroomActivity(Activity):
		pass

	class LeaveHomeActivity(Activity):
		pass

	class PersonnalHygieneActivity(Activity):
		pass

	class PhoneActivity(Activity):
		pass

	class ReadActivity(Activity):
		pass

	class RelaxActivity(Activity):
		pass

	class SleepActivity(Activity):
		pass

	class SleepOutOfBedActivity(Activity):
		pass

	class ToiletActivity(Activity):
		pass

	class WashDishesActivity(Activity):
		pass

	class WashBreakfastDishesActivity(WashDishesActivity):
		pass

	class WashDinnerDishesActivity(WashDishesActivity):
		pass

	class WashLunchDishesActivity(WashDishesActivity):
		pass

	class WatchTVActivity(Activity):
		pass

	class WorkAtTableActivity(Activity):
		pass

	class Device(Thing): 
		pass

	class Location(Thing): 
		pass

	class Measure(Thing): 
		pass

	class Property(Thing):
		pass

	class hasLocation(Device >> Location, FunctionalProperty): 
		python_name = "location"

	class isEmbeddedBy(Sensor >> Device, FunctionalProperty):
		pass

	class embeds(Device >> Sensor, InverseFunctionalProperty):
		python_name = "sensors"
		inverse_property = isEmbeddedBy

	class isMeasuredBy(Measure >> Sensor, FunctionalProperty): 
		python_name = "sensor"

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

	class correlatesWith(Sensor >> Property): 
		pass


SENSOR_TYPE_TRANSLATION = {
	'BA':BatterySensor,
	'D':DoorSensor,
	'L':LightSwitchSensor,
	'LL':LightSwitchSensor,
	'LS':LightSensor,
	'M':MotionSensor,
	'MA':WideAreaMotionSensor,
	'T':TemperatureSensor
}

ACTIVITY_EVENT = {
	'begin':beginsAt, 
	'end':endsAt, 
	None: hasTimeStamp
}

ACTIVITY_TYPE_TRANSLATION = {
	"Bathe":BathActivity, 
	"Bed_Toilet_Transition":BedToiletTransitionActivity, 
	"Cook": CookActivity, 
	"Cook_Breakfast": CookBreakfastActivity, 
	"Cook_Dinner": CookDinnerActivity,
	"Cook_Lunch": CookLunchActivity,
	"Dress": DressActivity, 
	"Eat": EatActivity,
	"Eat_Breakfast": EatBreakfastActivity,
	"Eat_Lunch": EatLunchActivity,
	"Eat_Dinner": EatDinnerActivity,
	"Enter_Home": EnterHomeActivity, 
	"Entertain_Guests": EntertainGuestsActivity,
	"Evening_Meds": TakeEveningMedsActivity, 
	"Groom":GroomActivity,
	"Leave_Home":LeaveHomeActivity,
	"Morning_Meds":TakeMorningMedsActivity,
	"Personal_Hygiene":PersonnalHygieneActivity,
	"Phone": PhoneActivity,
	"Read": ReadActivity,
	"Relax": RelaxActivity,
	"Sleep": SleepActivity,
	"Sleep_Out_Of_Bed": SleepOutOfBedActivity,
	"Toilet": ToiletActivity,
	"Wash_Dishes": WashDishesActivity,
	"Wash_Breakfast_Dishes": WashBreakfastDishesActivity,
	"Wash_Lunch_Dishes": WashLunchDishesActivity,
	"Wash_Dinner_Dishes": WashDinnerDishesActivity,
	"Watch_TV": WatchTVActivity,
	"Work_At_Table": WorkAtTableActivity
}

MEASURE_TYPE_TRANSLATION = {
	'open': True, 
	'close': False, 
	'on': True, 
	'off': False
}

ROOMS_DESCRIPTION = { # To discover / self organization ? 
}