import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core import MotorCADError
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import math
import json

# Retain pyqt4 compatibility
import os
if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"
    
mcad = pymotorcad.MotorCAD()

mcad.set_variable('MessageDisplayState', 2) # Ensure Motor-CAD does not create any dialogs requesting user response

# read_parameters function allows to import the initial settings from a json file
def read_parameters(json_file):
    with open(json_file, "r") as f:
        param_dict = json.load(f)
    return param_dict

json_file ='C:/Workspace/pymotorCAD/testing/ECE_config.json'
in_data = read_parameters(json_file)
mot_file = in_data["mot_file"]
shaft_speed = in_data["shaft_speed"]
dc_bus_voltage = float(in_data["dc_bus_voltage"])
machine_temp = float(in_data["machine_temp"])
Id_max = float(in_data["Id_max"])
current_step = float(in_data["current_step"])
map_name = in_data["map_name"]
txt_file = in_data["txt_file"]
sml_file = in_data["sml_file"]

#I. Input Settings

mcad.load_from_file(mot_file)

#II. Alignment Angle Detection

PointsPerCycle = 30
mcad.set_variable("DCBusVoltage", dc_bus_voltage)
mcad.set_variable('ArmatureConductor_Temperature', machine_temp)
mcad.set_variable('Magnet_Temperature', machine_temp)
mcad.set_variable('Shaft_Temperature', machine_temp)
mcad.set_variable('CurrentDefinition', 0)
mcad.set_variable('MagneticThermalCoupling', 0)
mcad.set_variable('BackEMFCalculation', True)
mcad.set_variable('TorquePointsPerCycle', PointsPerCycle)
mcad.set_variable('ShaftSpeed', shaft_speed)
mcad.set_variable('PeakCurrent', 0)
mcad.set_variable('CoggingTorqueCalculation', False)
mcad.set_variable('TorqueCalculation', False)
mcad.set_variable('TorqueSpeedCalculation', False)
try:
    mcad.do_magnetic_calculation()
except MotorCADError:
    mcad.show_message("Calculation Failed")

#II.a A-Phase FluxLinkage plot

EDeg=[]
FluxA=[]
indexf=PointsPerCycle
for n in range(indexf+1):
    xa, ya = mcad.get_magnetic_graph_point("FluxLinkageOCPh1", n)
    EDeg.append(xa)
    FluxA.append(ya)

#II.b Calculation of TorquePointsPerCycle

p=mcad.get_variable('Pole_Number')
drive=mcad.get_variable('DriveOffsetAngleLoad')
PhaseRes=mcad.get_variable('ArmatureWindingResistancePh')
PhaseL=mcad.get_variable('EndWdgInductance_Used')
drive_offset=90+drive
p=p/2
max_elec_degree=120
# Factor function
fac=[]
d=2
n=drive_offset
while n>=d:
    if n%d ==0:
        fac.append(d)
        n /=d
    else:
        d=d+1

fac_size=len(fac)
elecdeg=fac[fac_size-1]
i=1
while (max_elec_degree/elecdeg)<30:
    elecdeg=fac[fac_size-1-i]
    i=i+1  
m_period=max_elec_degree/p
mecdeg=float(float(elecdeg)/float(p))  
PointsPerCycle=360/elecdeg

# III. Saturation Map Calculation


mcad.set_variable('TorquePointsPerCycle', PointsPerCycle)
mcad.set_variable('SaturationMap_ExportFile', map_name)
mcad.set_variable('SaturationMap_InputDefinition', 1)
mcad.set_variable('SaturationMap_CalculationMethod', 1)
mcad.set_variable('SaturationMap_FEACalculationType', 1)
mcad.set_variable('SaturationMap_ResultType', 1)
mcad.set_variable('LossMap_Export', False)
mcad.set_variable('SaturationMap_Current_D_Max', Id_max)
mcad.set_variable('SaturationMap_Current_D_Step', current_step)
mcad.set_variable('SaturationMap_Current_D_Min', -Id_max)
mcad.set_variable('SaturationMap_Current_Q_Max', Id_max)
mcad.set_variable('SaturationMap_Current_Q_Step', current_step)
mcad.set_variable('SaturationMap_Current_Q_Min', -Id_max)

try:
    mcad.calculate_saturation_map()
except MotorCADError:
    mcad.show_message("Map calculation failed")

#Load Saturation Map

Mat_File_Data = scipy.io.loadmat(map_name)

Id_Peak = Mat_File_Data['Id_Peak']
Iq_Peak = Mat_File_Data['Iq_Peak']
Angular_Flux_Linkage_D = Mat_File_Data['Angular_Flux_Linkage_D']
Angular_Flux_Linkage_Q = Mat_File_Data['Angular_Flux_Linkage_Q']
Angular_Flux_Linkage_1 = Mat_File_Data['Angular_Flux_Linkage_Phase_1']
Angular_Flux_Linkage_2 = Mat_File_Data['Angular_Flux_Linkage_Phase_2']
Angular_Flux_Linkage_3 = Mat_File_Data['Angular_Flux_Linkage_Phase_3']
Angular_Rotor_Position = Mat_File_Data['Angular_Rotor_Position']
Angular_Electromagnetic_Torque = Mat_File_Data['Angular_Electromagnetic_Torque']
Phase_Advance = Mat_File_Data['Phase_Advance']
dvalues = len(Id_Peak)
qvalues = len(Id_Peak[0])
comb = dvalues*qvalues
MapPoints = int((max_elec_degree/elecdeg)+1)
RotPos = (max_elec_degree/p)+1
ind = 0
index_1 = []
Flux_D_2 = []
Flux_Q_3 = []
Flux_0_4 = []
Torque_5 = []
Id_6 = []
Iq_7 = []
Phase_ad_8 = []
Rotor_pos_9 = []
FinalTable = []
skip = math.ceil(drive_offset/elecdeg)

# IV.b Implementation of FinalTable

for i in range(dvalues):
    for j in range(qvalues):
        for k in range(int(skip), int(skip-MapPoints), (-1)):
            ind = ind+1
            if k < 0:
                kprimo = int(PointsPerCycle+k)
                index_1.append(ind-1)
                Flux_D_2.append(Angular_Flux_Linkage_D[i, j, kprimo])
                Flux_Q_3.append(Angular_Flux_Linkage_Q[i, j, kprimo])
                Flux_0_4.append(0)
                Torque_5.append(-Angular_Electromagnetic_Torque[i, j, kprimo])
                Id_6.append(Id_Peak[i, j])
                Iq_7.append(Iq_Peak[i, j])
                Phase_ad_8.append(Phase_Advance[i, j])
                Rotor_pos_9.append(Angular_Rotor_Position[i, j, kprimo])
            else:
                index_1.append(ind-1)
                Flux_D_2.append(Angular_Flux_Linkage_D[i, j, k])
                Flux_Q_3.append(Angular_Flux_Linkage_Q[i, j, k])
                Flux_0_4.append(0)
                Torque_5.append(-Angular_Electromagnetic_Torque[i, j, k])
                Id_6.append(Id_Peak[i, j])
                Iq_7.append(Iq_Peak[i, j])
                Phase_ad_8.append(Phase_Advance[i, j])
                Rotor_pos_9.append(Angular_Rotor_Position[i, j, k])
            
FinalTable = np.array([index_1, Flux_D_2, Flux_Q_3, Flux_0_4, Torque_5, Id_6, Iq_7, Phase_ad_8, Rotor_pos_9])


# V. Flux linkages and Torque plot
# V.a FluxD-Q plot 

plt.figure(1)
plt.plot(EDeg, FluxA)
plt.xlabel('Position [EDeg]')
plt.ylabel('FluxLinkageA')
plt.title('A_Phase Flux Linkage')
plt.show()

plt.figure(2)
plt.plot(index_1,Flux_D_2,'r',index_1,Flux_Q_3,'b',linewidth=1.0)
plt.xlabel('Points')
plt.ylabel('Flux [Vs]')
plt.legend(['Psid','Psiq'],loc='lower right')
plt.title('D-Q Flux')
plt.show()

# V.b Torque plot

plt.figure(3)
plt.plot(index_1,Torque_5, 'r',linewidth=2.0)
plt.ylabel('Torque [Nm]')
plt.xlabel('Points')
plt.title('Torque')
plt.show()

# V.c Flux Linkages vs q-axis current

plt.figure(3)
for i in range(dvalues):
    plt.plot(Iq_Peak[0,:],Angular_Flux_Linkage_Q[i,:,(skip)],label='Id='+str(Id_Peak[i,0])+'A')
plt.ylabel('Flux [Vs]')
plt.xlabel('Iq [A]')
plt.legend(fontsize=8,loc='lower right')
plt.title('D-Flux vs Iq')   
plt.show()

plt.figure(4)
for i in range(dvalues):
    plt.plot(Iq_Peak[0,:],Angular_Flux_Linkage_D[:,i,(skip)],label='Id='+str(Id_Peak[i,0])+'A')
plt.legend(fontsize=8,loc='lower right')
plt.ylabel('Flux [Vs]')
plt.xlabel('Iq [A]')
plt.title('Q-Flux vs Iq')   
plt.show()

# VI. .sml and .txt files creation
# VI.a Writing the .txt text

rows=len(index_1)

fileID=open(txt_file,'w')
fileID.write('%6s\r\n'%('B_BasicData'))
fileID.write('%6s\r\n'%('  Version   1.0'))
fileID.write('%6s %i\r\n'%('  Poles', p*2))
fileID.write('%6s\r\n\n'%('E_BasicData'))

fileID.write('%6s\r\n'%('B_PhaseImp 3'))
fileID.write('%6s %12.10e %s %12.10e\r\n'%('    WG_Ph1', PhaseRes,'    ',PhaseL))
fileID.write('%6s %12.10e %s %12.10e\r\n'%('    WG_Ph2', PhaseRes,'    ',PhaseL))
fileID.write('%6s %12.10e %s %12.10e\r\n'%('    WG_Ph3', PhaseRes,'    ',PhaseL))
fileID.write('%6s\r\n\n'%('E_PhaseImp'))

fileID.write('%6s\r\n\n'%('B_Sweepings'))
fileID.write('%s %i %s'%('  Id_Iq     (',dvalues,':'))
for i in range(dvalues):
    fileID.write('%s %i'%(' ',Id_Peak[i,0]))
fileID.write('%s\n'%(')'))

fileID.write('%s %i %s'%('            (',qvalues,':'))
for i in range(qvalues):
    fileID.write('%s %i'%(' ',Iq_Peak[0,i]))
fileID.write('%s\n'%(')'))

fileID.write('%s %i %s'%('  Rotate    (',MapPoints,':'))

for i in range(MapPoints):
    fileID.write('%s %6.3f'%(' ',i*mecdeg))
fileID.write('%s\n'%(')'))
fileID.write('%s\n\n'%('E_Sweepings'))

fileID.write('%s\n'%('B_OutputMatrix DQ0'))

for i in range(rows):
    fileID.write('%10i %19.10e %19.10e %19.10e %19.10e\r\n'%(index_1[i],Flux_D_2[i],Flux_Q_3[i],Flux_0_4[i],Torque_5[i]))
fileID.write('%s\n'%('E_OutputMatrix'))

fileID.close()


# VI.b Writing the .sml file

fileID=open(sml_file,'w')
fileID.write('%6s\r\n'%('MODELDEF ECER_Model1'))
fileID.write('%s\r\n'%('{'))
fileID.write('%6s\r\n'%('PORT electrical: A0;'))
fileID.write('%6s\r\n'%('PORT electrical: X0;'))
fileID.write('%6s\r\n'%('PORT electrical: B0;'))
fileID.write('%6s\r\n'%('PORT electrical: Y0;'))
fileID.write('%6s\r\n'%('PORT electrical: C0;'))
fileID.write('%6s\r\n'%('PORT electrical: Z0;'))
fileID.write('%6s\r\n'%('PORT ROTATIONAL_V: ROT1;'))
fileID.write('%6s\r\n'%('PORT ROTATIONAL_V: ROT2;'))

fileID.write('%6s%4.3f%s\r\n'%('PORT REAL IN: ra0 = ',PhaseRes,';'))
fileID.write('%6s%4.0e%s\r\n'%('PORT REAL IN: la0 = ',PhaseL,';'))
fileID.write('%6s\r\n'%('PORT REAL IN: IniIa0 = 0;'))
fileID.write('%6s\r\n'%('PORT REAL IN: IniIb0 = 0;'))
fileID.write('%6s\r\n'%('PORT REAL IN: IniIc0 = 0;'))
fileID.write('%6s\r\n'%('PORT REAL OUT: Fluxa0 = AM_Fluxa0.I;'))
fileID.write('%6s\r\n'%('PORT REAL OUT: Fluxb0 = AM_Fluxb0.I;'))
fileID.write('%6s\r\n'%('PORT REAL OUT: Fluxc0 = AM_Fluxc0.I;'))
fileID.write('%6s\r\n'%('PORT REAL OUT: Fluxd0 = AMFd.I;'))
fileID.write('%6s\r\n'%('PORT REAL OUT: Fluxq0 = AMFq.I;'))

fileID.write('%6s\r\n'%('PORT REAL IN ANGLE[deg]: IniPos = 0;'))
fileID.write('%6s\r\n\n'%('PORT REAL OUT ANGLE[deg]: Pos = VM_Mdeg.V;'))

fileID.write('%6s\r\n'%('INTERN  R        Ra0  N1:=A0, N2:=N_1  ( R:=ra0 );'))
fileID.write('%6s\r\n'%('INTERN  L        La0  N1:=N_1, N2:=N_2  ( L:=la0, I0:=IniIa0 );'))
fileID.write('%6s\r\n'%('INTERN  AM       AMa0  N1:=N_2, N2:=N_3  ;'))
fileID.write('%6s\r\n'%('INTERN  EV       Ema0  N1:=N_3, N2:=X0  ( QUANT:=VMa0.V, FACT:=-1 ); '))
fileID.write('%6s\r\n'%('INTERN  L        Lma0  N1:=N_4, N2:=GND  ( L:=1 ); '))
fileID.write('%6s\r\n'%('INTERN  VM       VMa0  N1:=N_4, N2:=GND  ; '))
fileID.write('%6s\r\n'%('INTERN  AM       AM_Fluxa0  N1:=N_5, N2:=N_4  ; '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxad  N1:=GND, N2:=N_5  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxaq  N1:=GND, N2:=N_5  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxao  N1:=GND, N2:=N_5  ( QUANT:=AMFo.I, FACT:=1 ); '))
fileID.write('%6s\r\n\n'%('INTERN  II       Fluxa0  N1:=GND, N2:=N_5  ( QUANT:=AMo.I, FACT:=0 ); '))

fileID.write('%6s\r\n'%('INTERN  R        Rb0  N1:=B0, N2:=N_6  ( R:=ra0 ); '))
fileID.write('%6s\r\n'%('INTERN  L        Lb0  N1:=N_6, N2:=N_7  ( L:=la0, I0:=IniIb0 );'))
fileID.write('%6s\r\n'%('INTERN  AM       AMb0  N1:=N_7, N2:=N_8  ; '))
fileID.write('%6s\r\n'%('INTERN  EV       Emb0  N1:=N_8, N2:=Y0  ( QUANT:=VMb0.V, FACT:=-1 );  '))
fileID.write('%6s\r\n'%('INTERN  L        Lmb0  N1:=N_9, N2:=GND  ( L:=1 ); '))
fileID.write('%6s\r\n'%('INTERN  VM       VMb0  N1:=N_9, N2:=GND  ; '))
fileID.write('%6s\r\n'%('INTERN  AM       AM_Fluxb0  N1:=N_10, N2:=N_9  ; '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxbd  N1:=GND, N2:=N_10  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V-2*PI/3) );'))
fileID.write('%6s\r\n'%('INTERN  II       Fluxbq  N1:=GND, N2:=N_10  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V-2*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxbo  N1:=GND, N2:=N_10  ( QUANT:=AMFo.I, FACT:=1 ); '))
fileID.write('%6s\r\n\n'%('INTERN  II       Fluxb0  N1:=GND, N2:=N_10  ( QUANT:=AMo.I, FACT:=0 ); '))

fileID.write('%6s\r\n'%('INTERN  R        Rc0  N1:=C0, N2:=N_11  ( R:=ra0 ); '))
fileID.write('%6s\r\n'%('INTERN  L        Lc0  N1:=N_11, N2:=N_12  ( L:=la0, I0:=IniIc0 ); '))
fileID.write('%6s\r\n'%('INTERN  AM       AMc0  N1:=N_12, N2:=N_13  ;  '))
fileID.write('%6s\r\n'%('INTERN  EV       Emc0  N1:=N_13, N2:=Z0  ( QUANT:=VMc0.V, FACT:=-1 ); '))
fileID.write('%6s\r\n'%('INTERN  L        Lmc0  N1:=N_14, N2:=GND  ( L:=1 ); '))
fileID.write('%6s\r\n'%('INTERN  VM       VMc0  N1:=N_14, N2:=GND  ;'))
fileID.write('%6s\r\n'%('INTERN  AM       AM_Fluxc0  N1:=N_15, N2:=N_14  ;'))
fileID.write('%6s\r\n'%('INTERN  II       Fluxcd  N1:=GND, N2:=N_15  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V-4*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxcq  N1:=GND, N2:=N_15  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V-4*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Fluxco  N1:=GND, N2:=N_15  ( QUANT:=AMFo.I, FACT:=1 ); '))
fileID.write('%6s\r\n\n'%('INTERN  II       Fluxc0  N1:=GND, N2:=N_15  ( QUANT:=AMo.I, FACT:=0 );'))

fileID.write('%6s\r\n'%('INTERN  AM       AMFd  N1:=N_16, N2:=GND  ; '))
fileID.write('%6s\r\n'%('INTERN  AM       AMFq  N1:=N_17, N2:=GND  ;'))
fileID.write('%6s\r\n\n'%('INTERN  AM       AMFo  N1:=N_18, N2:=GND  ; '))

fileID.write('%6s\r\n'%('INTERN  II       Id0  N1:=GND, N2:=N_19  ( QUANT:=AMa0.I, FACT:=2/3*cos(VM_Erad.V) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Id1  N1:=GND, N2:=N_19  ( QUANT:=AMb0.I, FACT:=2/3*cos(VM_Erad.V-2*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Id2  N1:=GND, N2:=N_19  ( QUANT:=AMc0.I, FACT:=2/3*cos(VM_Erad.V-4*PI/3) );'))
fileID.write('%6s\r\n'%('INTERN  AM       AM0  N1:=N_19, N2:=GND  ;'))
fileID.write('%6s\r\n'%('INTERN  II       Iq0  N1:=GND, N2:=N_20  ( QUANT:=AMa0.I, FACT:=2/3*sin(VM_Erad.V) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Iq1  N1:=GND, N2:=N_20  ( QUANT:=AMb0.I, FACT:=2/3*sin(VM_Erad.V-2*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  II       Iq2  N1:=GND, N2:=N_20  ( QUANT:=AMc0.I, FACT:=2/3*sin(VM_Erad.V-4*PI/3) ); '))
fileID.write('%6s\r\n'%('INTERN  AM       AM1  N1:=N_20, N2:=GND  ; '))
fileID.write('%6s\r\n'%('INTERN  II       I00  N1:=GND, N2:=N_21  ( QUANT:=AMa0.I, FACT:=1/3 ); '))
fileID.write('%6s\r\n'%('INTERN  II       I01  N1:=GND, N2:=N_21  ( QUANT:=AMb0.I, FACT:=1/3 ); '))
fileID.write('%6s\r\n'%('INTERN  II       I02  N1:=GND, N2:=N_21  ( QUANT:=AMc0.I, FACT:=1/3 ); '))
fileID.write('%6s\r\n\n'%('INTERN  AM       AMo  N1:=N_21, N2:=GND  ; '))

fileID.write('%6s\r\n'%('INTERN  VM       VM_Speed  N1:=N_23, N2:=N_22  ; '))
fileID.write('%6s\r\n'%('UMODEL  D2D      D2D1 N1:=N_23, N2:=ROT1 ( NATURE_1:="electrical", NATURE_2:="Rotational_V" ) SRC: DLL( File:="Domains.dll");'))
fileID.write('%6s\r\n'%('UMODEL  D2D      D2D2 N1:=N_22, N2:=ROT2 ( NATURE_1:="electrical", NATURE_2:="Rotational_V" ) SRC: DLL( File:="Domains.dll");'))
fileID.write('%6s\r\n'%('INTERN  IV       Gx  N1:=GND, N2:=N_24  ( QUANT:=VM_Speed.V, FACT:=57.29578 ); '))
fileID.write('%6s\r\n'%('INTERN  C        Cx  N1:=N_24, N2:=GND  ( C:=1, V0:=IniPos ); '))
fileID.write('%6s\r\n'%('INTERN  VM       VM_Mdeg  N1:=N_24, N2:=GND  ; '))
fileID.write('%6s\r\n'%('INTERN  IV       Ipos  N1:=GND, N2:=N_25  ( QUANT:=VM_Mdeg.V, FACT:=1 ); '))
fileID.write('%6s\r\n'%('INTERN  AM       AM2  N1:=N_25, N2:=N_26  ; '))
fileID.write('%6s %8.7f %s\r\n'%('INTERN  R        Rpos  N1:=N_26, N2:=GND  ( R:=',0.0174533*p,' ); '))
fileID.write('%6s\r\n\n'%('INTERN  VM       VM_Erad  N1:=N_26, N2:=GND  ;'))

fileID.write('%6s\r\n'%('INTERN  NDSRC    PECER_Model1  N0:=GND, N1:=N_16, N2:=GND, N3:=N_17, N4:=GND, N5:=N_18, N6:=N_22, N7:=N_23 \ '))
fileID.write('%6s\r\n'%(' ( QUANT:={ AM0.I, AM1.I, AM2.I }, SRC:={ isrc, isrc, isrc, isrc }, TableData:="\ '))
fileID.write('%6s'%('.MODEL ECER_Model1_table pwl TABLE=('))
fileID.write('%s%u%s'%(' ',dvalues,','))

index=0

for i in range(dvalues):
    fileID.write('%s%d'%(' ',Id_Peak[i,0]))
    fileID.write('%s'%(','))
    if i==(dvalues-1):
        fileID.write('%s\n'%('\ '))
        fileID.write('%s'%(' 0,'))
        
for r in range(dvalues):
    fileID.write('%s%u%s'%(' ',qvalues,','))
    for i in range(qvalues):
        fileID.write('%s%d'%(' ',Iq_Peak[0,i]))
        fileID.write('%s'%(','))
        if i == (qvalues-1):
            fileID.write('%s\n'%('\ '))
            fileID.write('%s'%(' 0,'))
        
    for k in range(qvalues):
        fileID.write('%s%u%s'%(' ',MapPoints,','))
        for i in range(MapPoints):
            fileID.write('%s%6.3f'%(' ',i*mecdeg))
            fileID.write('%s'%(','))
            if i == (MapPoints-1):
                fileID.write('%s\n'%('\ '))
                fileID.write('%s'%(' 4,')) 
                
        for j in range(1,5):
            for i in range(MapPoints):
                fileID.write('%s%f'%(' ',FinalTable[int(j),int(index+i)]))
                fileID.write('%s'%(',')) 
                if r == (dvalues-1) and k == (qvalues-1) and j==4 and i == (MapPoints-1):
                    fileID.write('%s\r\n'%(') LINEAR LINEAR PERIODIC\ '))
                    fileID.write('%s\r\n'%(' DEEPSPLINE" );'))
                    fileID.write('%s\r\n'%('}'))
                elif i == (MapPoints-1):
                    fileID.write('%s\n'%('\ '))
        index=index+(MapPoints)

fileID.close()
mcad.quit()