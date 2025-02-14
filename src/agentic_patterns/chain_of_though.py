from crewai.flow.flow import Flow,start,listen,router,or_
from litellm import completion
import os
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL")
customer_email = (
    "Hi, I recently purchased a laptop from your store, but it has been malfunctioning. "
    "I am very disappointed with the quality and would like to know what can be done about it."
)
class CustomerSupport(Flow):
    """
    First LLM Call:extract the issue from the customer email
    """
    @start()
    def extract_issue(self):
        response = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=[
                {"role":"system","content":"You are a customer support agent. Your task is to extract the issue from the customer email."},
                {"role":"user","content":f"Extract the main issue and concerns from the following customer email: {	customer_email}"},
            ]
        )
        issue = response.choices[0].message.content.strip()
        self.state["issue"] = issue
        #print(f"Extracted issue: {issue}")
        return issue
    @listen(extract_issue)
    def genrate_draft_response(self):
        """
        Second LLM Call:Draft a response to the customer email
        """	
        issue = self.state["issue"]
        response = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=[
                {"role":"system","content":"You are a customer support agent. Your task is draft a response to the customer email."},
                {"role":"user","content":f"draft a reposnce adressing the following cutomer issue: {issue} ensure the reponse is clear ,professional and empathetic"},
            ]
        )
        draft_response = response.choices[0].message.content.strip()
        self.state["draft_response"] = draft_response
        #print(f"Generated solution: {solution}")
        return draft_response
    @router(genrate_draft_response)
    def check_response(self):
        """
        Gate function to check if the draft response included empathic language
        A simple check would look for word like 'sorry' or 'apologies'
        """
        draft_response = self.state["draft_response"]
        if "sorry" in draft_response.lower() or "apologies" in draft_response.lower():
            #print("Response is empathic. Proceeding to next step.")
            return "sucess"
        else:
            #print("Response is not empathic. Re-drafting response.")
            return "failure"	
    @listen("failure")
    def re_draft_response(self):
        """
        Third LLM Call:Re-draft the response to include empathic language
        """
        draft_response = self.state["draft_response"]
        response = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=[
                {"role":"system","content":"You are a customer support agent. Your task is to re-draft the response to include empathic language."},
                {"role":"user","content":f"Re-draft the following response to include empathic language: {draft_response} rewrite it to better express the customer's concern"},
            ]
        )
        re_drafted_response = response.choices[0].message.content.strip()
        self.state["re_drafted_response"] = re_drafted_response
        return re_drafted_response
    @or_("sucess",re_draft_response)
    def polish_response(self):
        """
        Fourth LLM Call:Polish the response to make it more engaging and professional
        """
        response = self.state["re_drafted_response"]
        response = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=[
                {"role":"system","content":"You are a customer support agent. Your task is to polish the response to make it more engaging and professional."},
                {"role":"user","content":f"Polish the following response to make it more engaging and professional: {response}"},
            ]
        )
        polished_response = response.choices[0].message.content.strip()
        self.state["polished_response"] = polished_response
        return polished_response
    @listen(polish_response)
    def write_to_file(self):
        """
        Fifth LLM Call:Write the polished response to a file
        """
        polished_response = self.state["polished_response"]
        with open("response.txt","w") as file:
            file.write(polished_response)
        print(f"Response written to file: response.txt")
        return "response_written"
    
def main():
    obj=CustomerSupport()
    obj.kickoff()


def plot():
    obj=CustomerSupport()
    obj.plot()

