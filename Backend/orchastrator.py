
# Import libraries
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.identity import get_bearer_token_provider
import os
import re

def getOpenAIClient(token_provider):
    print("token_provider", token_provider)
    return AzureOpenAI(
        api_version=os.getenv("AZURE_OPENAI_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider
    ) 

    


def funcCall(user_query, openai_client, deployment_name):
    # Provide instructions to the model
    GROUNDED_PROMPT="""
        You are an expert SQL query generator for the following table:

Table name: v_PROD_INSPECT
Description: Stores raw material, tooling, and product-related information, including inspection results, quality data, and product specification related to Pressing Process at Orwel Plant.

Columns and Definitions:
(Order_number: Represents a batch of products)
(DIECASE_Equipment_ID: Equipment Id is same as equipment number and represents a unique Diecase)
(BOTPUNCH_Equipment_ID: Equipment Id is same as equipment number and represents a unique Bottom punch)
(TOPPUNCH_Equipment_ID: Equipment Id is same as equipment number and represents a unique Top Punch)
(Batch: Batch number of Powder / Raw material used)
(Material_Number: SKU or Material number of the product)
(Confirmation_Entry_Date_and_Time: Timestamp (in EST) recorded after order completion)
(Operator_Id: Unique ID of each Pressing operator)
(Date: Date of Operation)
(Machine_ID: Machine number in operation identified locally)
(ANSI: Geometry of Insert represents dimensions in metric)
(ISO: Geometry of Insert represents dimensions in inches)
(BaseMaterial: Base grade or Ingredient of the Powder. E.g S113, K313, S125, S129, S105 etc)
(DIESET_Equipment_Number: Equipment number represents a unique Dieset)
(DIESET_Equipment_Description: This tag defines a Dieset. Comprises Dieset number, set number, and ANSI)
(DIESET_Material_Description: Description of Dieset with SKU/Dieset Material number of the Equipment)
(Join_id_historical_data: Used for specific joins to create historical comparisons of similar orders)
(Quantity_Confirmed: Total good pieces of products produced in pressing operation)
(Scrap_Quantity: Total scrap pieces of products produced in pressing operation)
(Deflash_HoneSpec: Target Edge radius of the product with tolerance)
(Grade: Properties of Insert, e.g., KCK15 represents product's hardness and end application)
(EPSCode: Code describing the Final Edge Condition of the product)
(End_Time_Order: End time of order)
(Cycle_time: Cycle Time of order in seconds)
(Cycle_time_formatted: Cycle Time of order formatted in HH:MM:SS)
(Average_cycle_time_per_insert: Average Cycle Time of pressing Per Insert in seconds for an order)
(cleaning_frequency: Cleaning interval representing number of inserts after which punches were cleaned)
(Flash_Height_micron: Measured flash height of inserts in microns during pressing inspections)
(Green_Thickness: Measured Thickness of inserts in mm during pressing inspections)
(Green_Weight: Measured Weight of inserts in grams during pressing inspections)
(Flash_Width: Measured width of inserts in mm during pressing inspections)
(Last_operation: Last process completed and recorded by operator in SAP MII)
(HE01_coerciveforce: Inspected Coercive force of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_linearshrinkfactorlsf: Inspected Linear Shrinkage factor of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_ms#nistd: Inspected Absolute Magnetic saturation (MS) of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_msnistd: Inspected Magnetic saturation percentage (MS) of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_normalizedhallflow: Inspected Hall flow or flowability of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_rockwellhardnessreferenceonly: Inspected material’s hardness based on the Rockwell hardness scale of Powder / Raw material Batch at powder manufacturing plant Henderson)
(HE01_scottdensityreferenceonly: Inspected apparent density of Powder / Raw material Batch at powder manufacturing plant Henderson)
(OR01_density1185: Density of powder at 1.187 die factor. Deprecated, use OR01_density1200)
(OR01_density1200: Density of powder at 1.2 die factor)
(OR01_linearshrinkfactorlsf: Inspected Linear Shrinkage factor of Power / Raw material Batch received at Product manufacturing plant Orwell)
(OR01_ms: Inspected absolute Magnetic saturation (MS) of Power / Raw material Batch received at Product manufacturing plant Orwell)
(OR01_ms#: Inspected Magnetic saturation (MS) percentage of Power / Raw material Batch received at Product manufacturing plant Orwell)
(OR01_ms#1185: Inspected absolute Magnetic saturation (MS) of Power / Raw material Batch received at Product manufacturing plant Orwell at df 1.187. Deprecated, use OR01_ms#)
(OR01_ms1185: Inspected percentage Magnetic saturation (MS) of Power / Raw material Batch received at Product manufacturing plant Orwell at df 1.187. Deprecated, use OR01_ms)
(OR01_rockwellhardnessreferenceonly: Inspected material’s hardness based on the Rockwell hardness scale of Power / Raw material Batch received at Product manufacturing plant Orwell)
(OR01_scottdensity: Inspected apparent density of Power / Raw material Batch received at Product manufacturing plant Orwell)
(OR01_thicknessshrinkfactor1185: Inspected Linear Shrinkage factor of Power / Raw material Batch received at Product manufacturing plant Orwell for Die factor 1.187. Deprecated, use OR01_thicknessshrinkfactor1200)
(OR01_thicknessshrinkfactor1200: Inspected Thickness Shrinkage factor of Powder / Raw material Batch received at Product manufacturing plant Orwell for Die factor 1.2)
(OR01_weightlossfactor: Inspected weight loss factor of Power / Raw material Batch received at Product manufacturing plant Orwell for Die factor 1.2)
(TOPPUNCH_Equipment_Number: Equipment number represents a unique Top Punch)
(InspectionDateTopEdge: Date of edge Inspection of top punch of the dieset)
(DieInspectionTopEdge: Inspection Reason of edge Inspection of top punch of the dieset)
(RamNumberTopEdge: Ram Number of dieset for edge Inspection of top punch)
(InspectionTypeTopEdge: Inspection Type of edge Inspection of top punch of the dieset)
(MeasurementLocationTopEdge: Measurement locations of edge Inspection of top punch of the dieset)
(RadiusTop: Mean radius of mean edge of Top Punch)
(BOTTOMPUNCH_Equipment_Number: Equipment number represents a unique Bottom Punch)
(InspectionDateBotEdge: Date of edge Inspection of Bottom punch of the dieset)
(DieInspectionBotEdge: Inspection Reason of edge Inspection of Bottom punch of the dieset)
(RamNumberBotEdge: Ram Number of dieset for edge Inspection of Bottom punch)
(InspectionTypeBotEdge: Inspection Type of edge Inspection of Bottom punch of the dieset)
(MeasurementLocationBotEdge: Measurement locations of edge Inspection of Bottom punch of the dieset)
(RadiusBot: Mean radius of mean edge of Bottom Punch)
(InspectionDateTopSurface: Date of surface roughness Inspection of top punch of the dieset)
(DieInspectionTopSurface: Inspection Reason of surface roughness Inspection of top punch of the dieset)
(RamNumberTopSurface: Ram Number of dieset for surface roughness Inspection of top punch)
(InspectionTypeTopSurface: Inspection Type of surface roughness Inspection of top punch of the dieset)
(MeasurementLocationTopSurface: Measurement locations of surface roughness Inspection of top punch of the dieset)
(AvgRoughnessProfileTop: Average Roughness (Ra) of Equipment profile of Top Punch)
(InspectionDateBotSurface: Date of surface roughness Inspection of bottom punch of the dieset)
(DieInspectionBotSurface: Inspection Reason of surface roughness Inspection of bottom punch of the dieset)
(RamNumberBotSurface: Ram Number of dieset for surface roughness Inspection of bottom punch)
(InspectionTypeBotSurface: Inspection Type of surface roughness Inspection of bottom punch of the dieset)
(MeasurementLocationBotSurface: Measurement locations of surface roughness Inspection of bottom punch of the dieset)
(AvgRoughnessProfileBot: Average Roughness of Equipment profile of bottom Punch)
(Observation_ratio: Ratio used to define confidence on data being analyzed)
(Bad_data: If observation ratio is above a certain threshold then it is flagged as bad data)
(TopPunch_Running_Total: Total pieces pressed by Top punch since last repair)
(BotPunch_Running_Total: Total pieces pressed by Bottom punch since last repair)
(DieCase_Running_Total: Total pieces pressed by Die case punch since last repair)

Table name: v_PressDataProcess
Description: Stores IoT data captured during the insert pressing operations using Osterwalder and Dorst machines at the Orwell plant.

Columns and Definitions:
Order_number: Represents a batch of products
MachineNumberLocal: Machine number in operation (local)
FillHeightCorrection: Die case adjustment for insert thickness (mm)
PressForce: Force applied during pressing (KN)
ProgName: Program representing a batch of orders (tool/dieset)
TagTimestamp_UTC: Timestamp in UTC
OperatingMode: Machine operation mode (Osterwalder: 32=Setup, 64=Production; Dorst: 1=Setup, 3=Production)
PartWeight: Weight of insert in grams
Timestamp_est: Timestamp in EST
PressPositionA: Top punch position (mm)
PressPositionB: Die case position (mm)
press_stroke_time: Duration between two pressing strokes (seconds)
order_label: Unused
Date: Date of Pressing Operation
Join_id_historical_data: Used for joins for historical comparisons

Table name: v_DEFLASH_PROD_INSPECT
Description: Stores raw material, tooling, and product-related information—including inspection results, quality data, and product specifications captured during the insert deflashing operations at the Orwell Plant.

Columns and Definitions:
Order_number: Represents a batch of products
Deflash_InspectionDate: Inspection Date for inserts during Deflash process
Deflash_InsertNumber: Number of Inserts measured during inspection at deflash
Deflash_MeasurementLocation: Location on the insert measured after deflash
Deflash_Burr_height_rake: Burr/Flash Height measured at Deflash
Deflash_Burr_height_clearance: Burr/Flash Clearance measured at Deflash
Deflash_Points_in_tolerance: Points in tolerance measured at Deflash
Deflash_InspectionType: Identifies if deflash process was Auto or Manual
Deflash_Type: Program selected in Alicona device for measurements
Pressing_MeasurementLocation: Location on the insert measured during pressing
Pressing_Flash_Height_rake: Burr/Flash Height measured at pressing
Pressing_Flash_height_clearance: Burr/Flash Clearance measured at pressing
Pressing_Points_in_tolerance: Points in tolerance measured at pressing
Pressing_Flash_Width: Width of the flash produced during pressing (mm)
Deflash_Confirm_Qty: Number of pieces confirmed as good in deflash operation
Deflash_Reason_and_Scrap_List: List of all Scrap reasons and quantity in Deflash
Deflash_Total_Scrap: Total quantity of Scraps in Deflash process

Table name: v_DEFLASH_PROCESS
Description: Stores IoT data captured during the insert deflashing operations at the Orwell Plant.

Columns and Definitions:

MachineNumberSAP: Machine number in operation identified in SAP
MachineNumberLocal: Machine number in operation identified locally
TagTimeStamp_EST: Time stamp in EST
MtK_ProductName: Recipe Name
Order_number: Represents a batch of products
MtK_TransferTraySpeed: Speed of tray during its transfer
MtK_TransferTrayAcceleration: Acceleration of tray during its transfer
MtK_BrushSpeed_Top: Speed of brush while deflashing the top side of the insert
MtK_BrushSpeed_Btm: Speed of brush while deflashing the bottom side of the insert
MtK_BrushId_Top: Brush ID identifier while deflashing the top side of the insert
MtK_BrushId_Btm: Brush ID identifier while deflashing the bottom side of the insert
MtK_NumberofSteps_Top: Number of steps in which deflash is done for top side of the insert
MtK_NumberofSteps_Btm: Number of steps in which deflash is done for bottom side of the insert
MtK_DoubleSided: Indicator if the insert is double sided (True/False)
MtK_Step1Angle_Top to MtK_Step10Angle_Top: Tray angle for top deflash steps 1-10
MtK_Step1Depth_Top to MtK_Step10Depth_Top: Brush depth for top deflash steps 1-10
MtK_Step1Passes_Top to MtK_Step10Passes_Top: Number of passes for top deflash steps 1-10
MtK_Step1BlowOff_Top to MtK_Step10BlowOff_Top: Air blown over insert for top deflash steps 1-10
MtK_Step1Angle_Btm to MtK_Step10Angle_Btm: Tray angle for bottom deflash steps 1-10
MtK_Step1Depth_Btm to MtK_Step10Depth_Btm: Brush depth for bottom deflash steps 1-10
MtK_Step1Passes_Btm to MtK_Step10Passes_Btm: Number of passes for bottom deflash steps 1-10
MtK_Step1BlowOff_Btm to MtK_Step10BlowOff_Btm: Air blown over insert for bottom deflash steps 1-10
PROGRAM_NAME: Program name (insert shape, size, deflash settings)
STEP_1_DEPTH to STEP_10_DEPTH: Recommended reference/baseline of depth of brush (Feed) during steps 1-10
NUMBER_OF_STEPS: Recommended total number of steps for the deflash process
AverageValueDepth: Average of recommended depth for all steps combined for a selected program during deflash process

Instructions:

Generate a valid SQL query for the above tables based on the user’s request.
Only use the columns listed above.
If the user asks for a filter, aggregation, or join, use the appropriate columns and SQL syntax.
If the user’s request is ambiguous, ask for clarification.
Return only the SQL query, no explanations.
Example user requests:

"Show me the total Quantity_Confirmed for each Material_Number in the last month."
"List all batches where Scrap_Quantity is greater than 10."
"Get the average Cycle_time for each Operator_Id."
        Query: {query}        
    """
    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": GROUNDED_PROMPT.format(query=user_query)
            }
        ],
        model=deployment_name
    )

    raw_sql = response.choices[0].message.content.strip()

    # Remove markdown code block if present (```sql ... ```)
    cleaned_sql = re.sub(r"^```sql\s*|```$", "", raw_sql.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()
    cleaned_sql = cleaned_sql.replace("\\n", " ").replace("\n", " ").strip()

    return cleaned_sql


# main rag function
def mainApp(user_query, credential):
    print("token provider")
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    print("token provider:", token_provider)
    openai_client = getOpenAIClient(token_provider)
    print("openai_client:", openai_client)
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    query = funcCall(user_query, openai_client, deployment_name)
    return query

    
