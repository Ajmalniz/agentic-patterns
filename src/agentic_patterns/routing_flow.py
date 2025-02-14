from crewai.flow.flow import start,listen,router,Flow
from litellm import completion
import os
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL")

class SupportFlow(Flow):
    """
    A flow that routes customer support queries to the appropriate department.
    """
    @start()
    def User_query(self):
        # Get user input for their support query
        user_input = input("Please describe your issue: ")
        
        # Save to flow state
        self.state["user_query"] = user_input
        
        return user_input
    
    @router(User_query)
    def Routing_agent(self):
        input = self.state["user_query"]
        # Classify the user query into a department
        response = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=[
                {"role": "user", "content": f"here is the customer's query: {input} \n\n Analyze the customer's query and determine the category it belongs to. If the query is related to payments, invoices, or account charges, respond with 'billing'. If the query involves troubleshooting, software/hardware issues, or technical support, respond with 'technical'. If the query does not fit into these categories, respond with 'general'. Your output should be only one of these three words: billing, technical, or general"}
            ]
        )   
        # Save the response to flow state
        response = response.choices[0].message.content.strip()
        self.state["routing_response"] = response
        if response == "billing":
            return "billing"
        elif response == "technical":
            return "technical"
        else:
            return "general"
    @listen("billing")
    def Billing_Agent(self):
        print("Hello, I am the billing agent:")
        return "billing"    
    @listen("technical")
    def Technical_Agent(self):
        print("Hello, I am the technical agent:")
        return "technical"
    @listen("general")
    def General_Agent(self):
        print("Hello, I am the general agent:")
        return "general"



def main():
    flow = SupportFlow()
    flow.kickoff()

def plot():
    flow = SupportFlow()
    flow.plot()


