from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import Postgresql
from diagrams.programming.language import Python
from diagrams.custom import Custom
from diagrams.saas.chat import Slack  # Using as generic chat/AI icon
from diagrams.onprem.client import Users
from diagrams.aws.general import InternetAlt2
from diagrams.programming.framework import Django
import os

# Ensure the output directory exists
output_dir = "visualization"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Change working directory to visualization so the file is generated there
os.chdir(output_dir)

graph_attr = {
    "fontsize": "45",
    "bgcolor": "transparent"
}

with Diagram("Investment Summary Generator Workflow", show=False, direction="LR", filename="investment_flow", graph_attr=graph_attr):
    
    # Roles
    user = Users("Admin / Trigger")

    # External Services
    with Cluster("External Services"):
        yahoo = InternetAlt2("Yahoo Finance\n(Market Data)")
        xai = InternetAlt2("X.AI (Grok)\n(LLM Analysis)")

    # Internal System
    with Cluster("Core System"):
        
        with Cluster("Processing Layer"):
            # Using Python icon for the service
            service = Python("Generator Service\n(Async/Parallel)")
            
        with Cluster("Data Layer"):
            db = Postgresql("PostgreSQL\n(Company/Summary)")

    # Flow Definitions
    
    # 1. Trigger
    user >> Edge(label="1. Start Task", color="firebrick", style="bold") >> service
    
    # 2. Basic Data
    service >> Edge(label="2. Query Profile") >> db
    db >> Edge(label="Return Static Info", style="dashed") >> service
    
    # 3. Market Data (Bidirectional)
    service >> Edge(label="3. Fetch Price/PE") >> yahoo
    yahoo >> Edge(label="Return Data", style="dashed") >> service

    # 4. AI Analysis (Bidirectional)
    service >> Edge(label="4. Send Prompt") >> xai
    xai >> Edge(label="5. Return Report", style="dashed") >> service

    # 5. Save Results
    service >> Edge(label="6. Save Summary", color="darkgreen", style="bold") >> db

print("Diagram generated in visualization/investment_flow.png")

