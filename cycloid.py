import math
import adsk.core, adsk.fusion, traceback

# Global variables to store parameter values
_rotor_radius = adsk.core.ValueCommandInput.cast(None)
_roller_radius = adsk.core.ValueCommandInput.cast(None)
_eccentricity = adsk.core.ValueCommandInput.cast(None)
_number_lobes = adsk.core.ValueCommandInput.cast(None)
_eccentric_diameter = adsk.core.ValueCommandInput.cast(None)
_number_drive_pins = adsk.core.ValueCommandInput.cast(None)
_drive_pin_diameter = adsk.core.ValueCommandInput.cast(None)
_drive_pin_pattern_diameter = adsk.core.ValueCommandInput.cast(None)
_rotor_thickness = adsk.core.ValueCommandInput.cast(None)
handlers = []
app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
def run(context):
    try:
        global app,ui
        app = adsk.core.Application.get()
        ui = app.userInterface

        ui.messageBox('Starting the command')
        cmdDef = ui.commandDefinitions.itemById('CycloidalRotor')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition('CycloidalRotor')

        onCommandCreated = CustomCommandCreatedEventHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        cmdDef.execute()

        adsk.autoTerminate(False)

    except Exception as e:
        if ui:
            ui.messageBox('Failed in run function:\n{}'.format(traceback.format_exc()))
        
class CustomCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed\n{}'.format(traceback.format_exc()))

class CustomCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _eccentricity,_number_lobes,_roller_radius,_rotor_radius,_eccentric_diameter,_number_drive_pins,_drive_pin_pattern_diameter,_drive_pin_diameter,_rotor_thickness
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            des = adsk.fusion.Design.cast(app.activeProduct)
            if not des:
                ui.messageBox("Design must be active when running this command!")
                return()
      
            defaultUnits = des.unitsManager.defaultLengthUnits
            global _units
            if defaultUnits =='in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'
            
     
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
      
            _rotor_radius = inputs.addValueInput("rotor_radius","Rotor Radius",_units,adsk.core.ValueInput.createByReal(4))
            _roller_radius = inputs.addValueInput("roller_radius","Roller Radius",_units,adsk.core.ValueInput.createByReal(.6))
            _rotor_thickness = inputs.addValueInput("rotor_thickness","Rotor Thickness",_units,adsk.core.ValueInput.createByReal(1))
            _eccentricity = inputs.addValueInput("eccentricity","Eccentricity",_units,adsk.core.ValueInput.createByReal(.15))
            _eccentric_diameter = inputs.addValueInput("eccentric_diameter","Eccentric Diameter",_units,adsk.core.ValueInput.createByReal(1))
            _number_lobes = inputs.addStringValueInput("number_lobes","Number of Lobes",str(11))
            _number_drive_pins = inputs.addStringValueInput("number_drive_pins","Number of drive pins",str(4))
            _drive_pin_diameter = inputs.addValueInput("drive_pin_diameter","Drive pin diameter",_units,adsk.core.ValueInput.createByReal(.8))
            _drive_pin_pattern_diameter = inputs.addValueInput("drive_pin_pattern_diameter","Drive pin pattern diameter",_units,adsk.core.ValueInput.createByReal(3.5))

            # Connect to the execute event
            onExecute = CustomExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            onInputChanged = CustomCommandInputChangeHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            onDestroy = CustomCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)

        except:
            if ui:
                ui.messageBox('Failed to create command inputs:\n{}'.format(traceback.format_exc()))

# Define the event handler for the execute event of the custom command
class CustomExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            des = adsk.fusion.Design.cast(app.activeProduct)
            attribs = des.attributes
            attribs.add("Cycloid",'rotor_radius',str(_rotor_radius.value))
            attribs.add("Cycloid","roller_radius",str(_roller_radius.value))
            attribs.add("Cycloid","eccentricity",str(_eccentricity.value))
            attribs.add("Cycloid","eccentric_diameter",str(_eccentric_diameter.value))
            attribs.add("Cycloid","number_lobes",str(_number_lobes.value))
            attribs.add("Cycloid","drive_pin_diameter",str(_drive_pin_diameter.value))
            attribs.add("Cycloid","drive_pin_pattern_diameter",str(_drive_pin_pattern_diameter.value))
            attribs.add("Cycloid","rotor_thickness",str(_rotor_thickness.value))
            rotor_radius = _rotor_radius.value 
            roller_radius = _roller_radius.value 
            rotor_thickness = _rotor_thickness.value
            eccentricity = _eccentricity.value 
            eccentric_diameter = _eccentric_diameter.value 
            number_lobes = int(_number_lobes.value) 
            number_drive_pins = int(_number_drive_pins.value)
            drive_pin_diameter = _drive_pin_diameter.value 
            drive_pin_pattern_diameter = _drive_pin_pattern_diameter.value 
            #get the cycloid arrays 
            X,Y = cycloidal_rotor(rotor_radius,roller_radius,eccentricity,number_lobes)
            # create a new component by creating an occurrence.
            occs = des.rootComponent.occurrences
            mat = adsk.core.Matrix3D.create()
            newOcc = occs.addNewComponent(mat)        
            newComp = adsk.fusion.Component.cast(newOcc.component)
            sketches = newComp.sketches
            # grab the xy plane
            xyPlane = newComp.xYConstructionPlane
            baseSketch = sketches.add(xyPlane)
            # Create sketch points based on the X, Y coordinates
            points = adsk.core.ObjectCollection.create()
            for i in range(len(X)):
                points.add(adsk.core.Point3D.create(X[i], Y[i], 0))
            spline = baseSketch.sketchCurves.sketchFittedSplines.add(points)
            spline.isClosed = True
            profile = baseSketch.profiles.item(0)
            extrudes = newComp.features.extrudeFeatures
            distance_value = adsk.core.ValueInput.createByReal(rotor_thickness)
            rotor_extrude = extrudes.addSimple(profile=profile,distance=distance_value,operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            rotor = rotor_extrude.bodies.item(0)
            rotor.name = "rotor"
            pinSketch = sketches.add(xyPlane)
            pinSketch.name = "drive_pins"
            # draw the drive pin pattern
            rotation_angle = math.radians(360/number_drive_pins)
            rad = drive_pin_pattern_diameter/2
            for i in range(number_drive_pins):
                x = rad * (math.cos(rotation_angle * i))
                y = rad * (math.sin(rotation_angle * i))
                pinSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x,y,0),(drive_pin_diameter/2) + (eccentricity/2))
            center_circle = pinSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), eccentric_diameter/2.0)
            profs = adsk.core.ObjectCollection.create()
            for prof in pinSketch.profiles:
                profs.add(prof)
            pins_extrude = extrudes.addSimple(profs,distance_value,adsk.fusion.FeatureOperations.CutFeatureOperation)
            pins_extrude.name = "pin cut"
            outer_pins = sketches.add(xyPlane)
            # draw pins
            rotation_angle = math.radians(360/(number_lobes))
            rad = rotor_radius
            for i in range(number_lobes):
                x = rad * (math.cos((rotation_angle * i) + rotation_angle/2)) + eccentricity
                y = rad * (math.sin((rotation_angle * i) + rotation_angle/2)) 
                outer_pins.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x,y,0),roller_radius)
            profs.clear()
            for prof in outer_pins.profiles:
                profs.add(prof)
            outer_pins_extrude = extrudes.addSimple(profs,distance_value,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            outer_pins_extrude.name = "outer pins"
            # extrude the rotor
            


        except Exception as e:
            if ui:
                ui.messageBox('Failed to execute command:\n{}'.format(traceback.format_exc()))
class CustomCommandInputChangeHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self,args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            _roller_radius.value = _roller_radius.value
            _rotor_radius.value = _rotor_radius.value
            _eccentricity.value = _eccentricity.value
            _drive_pin_diameter.value = _drive_pin_diameter.value
            _drive_pin_pattern_diameter.value = _drive_pin_pattern_diameter.value
            _number_drive_pins.value = _number_drive_pins.value
            _number_lobes.value = _number_lobes.value
            _eccentric_diameter.value = _eccentric_diameter.value
        except:
            if ui:
                ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

def cycloidal_rotor(R, R_r, E, N, num_points=300):
    X, Y = [], []
    for t in range(num_points):
        t = 2 * math.pi * t / num_points
        atan_term = math.atan2(math.sin((1 - N) * t), (R / (E * N)) - math.cos((1 - N) * t))
        X.append((R * math.cos(t)) - (R_r * math.cos(t + atan_term)) - (E * math.cos(N * t)))
        Y.append((-R * math.sin(t)) + (R_r * math.sin(t + atan_term)) + (E * math.sin(N * t)))
    return X, Y

