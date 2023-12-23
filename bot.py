from dotenv import load_dotenv
from time import sleep
import requests
import openai
import json
import os

class supertec_bot:

    def __init__(self):

        load_dotenv()
        self.client = openai.OpenAI(api_key=os.environ['openai_api_key'])
        self.assistant_id = "asst_3hc27jSOBuRwWx4dzDOUgAFt"

    def update_assistant(self):
        function_detail = {
            "type": "function",
            "function": {
                "name": "get_detail",
                "description": "Your first task is to gather data for all users, including their first and last names if available. Then, when another function is called, you should be called first so that you can provide the name along with the ID for the other function and then the other function can use the ID to retrieve the attendance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "retreive all the details of the employee"
                        }
                    },
                    "required": ["query"]
                }
            }
        }

        function_attendance = {
            "type": "function",
            "function": {
                "name": "get_attendance",
                "description": "Retrieve the attendance of the employee for the given month and year ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "the id of the employee"
                        },
                        "month": {
                            "type": "string",
                            "description": "the month of the attendance this can be any month of the year,This function will accept either Nov or November for the month, it won't work with the number 11."
                        },

                        "year": {
                            "type": "integer",
                            "description": "the year of the attendance this can be any year."
                        }
                        

                    },
                    "required": ["id", "month", "year"]
                }
            }
        }

        self.client.beta.assistants.update(
            self.assistant_id,
            name="Supertec Admin Support Chat Bot",
            instructions="You are a personal SuperTec Admin  support chatbot. your duty is to  provide all single information from supertec",
            tools=[function_attendance,function_detail],
            model="gpt-4-1106-preview",
        )

    def get_detail(query):
        headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0' }
        payload = {'company_token': 'II@tNfQ70O'}
        response = requests.post("https://superteclabs.com/apis2/retrieveallusers.php", data=payload,headers=headers)
        return response.text

    def get_attendance(self, id, month, year):
        headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0' }
        payload = {'company_token': 'II@tNfQ70O'}
        response = requests.get(f"https://superteclabs.com/apis2/AttendanceRecord.php?id={id}&month={month}&year={year}",headers=headers , data=payload )
        return response.text

    def user_chat(self, query):
        # Step 2: Create a Thread
        thread = self.client.beta.threads.create()
        print(f"Created thread with ID: {thread.id}")   

        # Step 3: Add a Message to a Thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Step 4: Run the Assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,    
            assistant_id=self.assistant_id,
            instructions=""
        )

        while run.status != 'completed':
            sleep(2)

            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"sttatus: {run.status}")

            if run.status == 'requires_action':
                tool_outputs = []
                for action in run.required_action.submit_tool_outputs.tool_calls:

                    func_name = action.function.name
                    arguments = json.loads(action.function.arguments)
                    print(f"Calling function: {func_name} with arguments: {arguments}")

                    try:
                        if func_name == "get_detail":
                            output = self.get_detail()
                            tool_outputs.append({
                                "tool_call_id": action.id,
                                "output": output
                            })

                        elif func_name == "get_attendance":
                            output = self.get_attendance(arguments['id'],arguments['month'],arguments['year'])
                            tool_outputs.append({
                                "tool_call_id": action.id,
                                "output": output
                            })    
                        else:
                            raise ValueError(f"Unknown function: {func_name}")

                    except Exception as e:
                        print(f"An error occurred while processing {func_name}: {e}")

                print("Submitting outputs back to the Assistant...")
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )

                answer = messages.data[0].content[0].text.value
                return answer
            
# abc = supertec_bot()
# abc.update_assistant()