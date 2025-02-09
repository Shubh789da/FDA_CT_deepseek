import streamlit as st
import sys
from io import StringIO
from groq import Groq
import os
import re
from dotenv import load_dotenv
import pandas as pd
from typing import Literal, TypedDict, Annotated
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
# from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from clinical_trials_module import get_clinical_trials_data
from openfda import Open_FDA
from context import fda_context, clinical_trial_context

# Set up environment variables
# os.environ["GROQ_API_KEY"]= st.secrets["GROQ_API_KEY"]
# os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
# os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
# os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["OPENAI_API_KEY"]=st.secrets["OPENAI_API_KEY"]
os.environ["GROQ_API_KEY"]= st.secrets["GROQ_API_KEY"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]


# Initialize Streamlit app
st.title("Clinical Trial and FDA Drug Data Analysis using DeepSeek 🐳")

if  'text' not in st.session_state:
    st.session_state.CONNECTED =  False
    st.session_state.text = ''

def _connect_form_cb(connect_status):
    st.session_state.CONNECTED = connect_status

def display_db_connection_menu():
    with st.form(key="connect_form"):
        st.text_input('Enter the condition', help='Click on search, pressing enter will not work', value=st.session_state.text, key='text')

        placeholder_for_domain = st.empty()
        with placeholder_for_domain:
            radio_option = st.radio("You are searching for", ["drug", "disease"], horizontal=True, key='domain', index = None)
        
        # Submit button inside the form
        submit_button = st.form_submit_button(label='Search',on_click=_connect_form_cb, args=(True,))

        # Handling the form submission
        if submit_button:
            if st.session_state.text == '':
                st.error("Please enter a condition")
                st.stop()

            if st.session_state.domain is None:
                st.error("Please select whether you are searching for drug or disease")
                st.stop()



display_db_connection_menu()

def fetch_open_fda(domain, keyword):
    """Fetch and cache Open FDA data based on the given domain and keyword."""
    return Open_FDA.open_fda_main(domain=domain, user_keyword=keyword)

if st.session_state.CONNECTED:
    # st.write('You are Searching for:',  st.session_state.text)

    # Load data and initialize session state
    if 'df' not in st.session_state:
        with st.spinner(f'🔍 Fetching clinical trials data for 🤒: **{st.session_state.text}**'):
            st.session_state.df_ct = get_clinical_trials_data(st.session_state.text)
                
        # Update status message
        st.success(f"✅ Clinical trials data fetched successfully for '{st.session_state.text}'!")
        
        with st.spinner(f"🔍Fetching FDA Data for💊:**{st.session_state.text}** "):
           st.session_state.df_fda = fetch_open_fda(domain=st.session_state.domain, keyword=st.session_state.text)
            # st.session_state.df_fda= pd.read_csv('apixaban_fda.csv')
        # Update status message
        st.success(f"✅ FDA drug data fetched successfully for '{st.session_state.text}'!")

        # st.session_state.context_ct = clinical_trial_context
        # st.session_state.context_fda = fda_context
        st.session_state.messages = []
        st.session_state.df = True

    #Display the dataframe
    st.write('Data Sample: Top 10 rows from the clinical trials data')
    st.dataframe(st.session_state.df_ct.head(10))
    st.write('Data Sample: Top 10 rows from the FDA drug data')
    st.dataframe(st.session_state.df_fda.head(10))

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "```text" in message["content"]:
                # Extract and display the code block properly
                code_content = message["content"].split("```text")[1].strip().strip("```")
                st.code(code_content, language='text')
            else:
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your clinical trial analysis question:"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        llm = ChatOpenAI(model="gpt-4o")

        # Prepare the graph state
        class MessageState(TypedDict):
            messages:Annotated[list[AnyMessage], add_messages]
            code: str
            result: str
            retry_count: int
            next: str
            dfs: list[str]
            out_df: any
            summary: str
            last_df_name: str
            pass

        class df_selection(TypedDict):
            """Dataframe selection: Choose one or more dataframes to query from."""
            df: list[Literal["clinical_trials_df", "FDA_drugs_df"]]  # Now df is a LIST

        

        def select_dataframe(state: MessageState) -> Command[Literal["generate_code"]]:
            """Dataframe selection node: Choose the dataframe(s) to query from."""

            dataframes = ["clinical_trials_df", "FDA_drugs_df"]

            df_selection_prompt = f"""Your task is to select relevant dataframes from {dataframes} based on the user query: 
                                    {state['messages'][-1]}. 
                                    - Choose either one or both dataframes as needed.
                                    - If the query requires information from both, return both in a list.
            """

            messages = [
                {"role": "system", "content": df_selection_prompt},
            ] + state["messages"]

            response = llm.with_structured_output(df_selection).invoke(messages)

            dfs = response["df"]

            # Ensure dfs is always a list (even if the model returns a single string)
            if isinstance(dfs, str):
                dfs = [dfs]

            return Command(goto="generate_code", update={"dfs": dfs})

        # Define the workflow functions
        def generate_code(state: MessageState) -> Command[Literal["agent"]]:
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            system_prompt = """Youa are a smart and intellegent heathcare Analyst. Your job is to Generate Python code that:
            - Uses only provided variables
            - Give the final dataframe from which answer to the query can be answered, and all the datafrmes in the code should have a suffix '_df
            - Includes any necessary imports
            - If fixing an error, correct the previous code while maintaining logic
            - While matching any name lower the case for the term to search and in data where to search
            - Also, try to use contains rather than exact match like ==
            """

            # Mapping of dataframe names to actual dataframes
            df_mapping = {
                "clinical_trials_df": st.session_state.df_ct,
                "FDA_drugs_df": st.session_state.df_fda
            }

            # Ensure we get the actual dataframes from the selected names
            data = [df_mapping[name] for name in state['dfs'] if name in df_mapping]
            # print(f'The lenth of data is: {len(data)}')

            if len(data)==1:
                # Determine the available variables
                available_variables = (
                    list(data.columns) if isinstance(data, pd.DataFrame) else
                    (list(data.keys()) if isinstance(data, dict) else 'N/A')
                )
                if state['dfs'][0] =='clinical_trials_df':
                    data_context = clinical_trial_context
                elif state['dfs'][0] == 'FDA_drugs_df':
                    data_context = fda_context

            else:
                data_context = fda_context + clinical_trial_context
                # Extract column names from each dataframe
                available_variables = {
                    name: list(df.columns) for name, df in zip(state['dfs'], data) if isinstance(df, pd.DataFrame)
                }

            # available_variables = list(st.session_state.df.columns)

            user_message =  f"""{data_context}
                Available variables: {available_variables}
                Dataframes available: {state['dfs']}
                Task: {state['messages'][-1]}"""


            # Error-based rectification request
            user_message_rectify = f"""The previous code:
                {state['code'] if isinstance(state.get('code'), str) else 'N/A'}

                gave the following error:
                {state['result']['error'] if isinstance(state.get('result', {}).get('error'), str) else 'N/A'}


                Based on the task: {state['messages'][-1]} and available variables: {available_variables},
                please fix the error while maintaining the original logic."""

            # Choose the correct prompt based on whether there's an error
            selected_message = user_message if not state.get('error') else user_message_rectify

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": selected_message}
                ],
                model="deepseek-r1-distill-llama-70b",
                temperature=0.1,
            )

            def clean_code_response(response):
                response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
                code_match = re.search(r'```python\n(.*?)```', response, flags=re.DOTALL)
                return code_match.group(1).strip() if code_match else response.strip()

            response = chat_completion.choices[0].message.content
            return Command(
                update={'code': clean_code_response(response)},
                goto= "agent"
            )

        def agent(state: MessageState) -> Command[Literal["summarize_result", "__end__"]]:
            # Access global variables safely
            data = state['dfs']

            # Check for the correct string values
            if data[0] == "clinical_trials_df":
                data_df = st.session_state.df_ct
            elif data[0] == "FDA_drugs_df":
                data_df = st.session_state.df_fda
            else:
                # Use a dictionary to store both DataFrames
                data_df = {
                    "clinical_trials_df": st.session_state.df_ct,
                    "FDA_drugs_df": st.session_state.df_fda
                }


            def execute_python(code, data=None):
                """Executes Python code with given context and prevents pandas truncation"""

                # Set pandas display options
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                pd.set_option('display.max_colwidth', None)

                old_stdout = sys.stdout
                sys.stdout = StringIO()

                # Ensure df is correctly assigned in the local scope
                local_vars = {"df": data_df} if isinstance(data_df, pd.DataFrame) else data_df

                local_vars = {'pd': pd,
                              '__builtins__': __builtins__
                            }
                
                if "clinical_trials_df" in data:
                    local_vars["clinical_trials_df"] = st.session_state.df_ct
                if "FDA_drugs_df" in data:
                    local_vars["FDA_drugs_df"] = st.session_state.df_fda


                try:
                    # Store initial variables
                    initial_vars = set(local_vars.keys())

                    exec(code, local_vars)

                    # Find all new DataFrame variables
                    new_vars = set(local_vars.keys()) - initial_vars
                    df_vars = {var: local_vars[var] for var in new_vars 
                            if isinstance(local_vars[var], pd.DataFrame)}
                    
                    # Get the last DataFrame created (if any exist)
                    result_df = None
                    if df_vars:
                        # Get the last DataFrame from the execution
                        # last_df_name = list(df_vars.keys())[-1]
                        # last_df_name= max(df_vars, key=lambda var: list(local_vars.keys()).index(var)) # Get the last created DF
                        last_df_name = re.findall(r'\b\w+_df\b', code)[-1]
                        result_df = df_vars[last_df_name]
                        print(f"\nCapturing DataFrame: '{last_df_name}'")


                    output = sys.stdout.getvalue()
                    return {
                            "output": output,
                            "error": None,
                            "result_df": result_df,
                            "all_dataframes": df_vars,  # Optional: return all DataFrames if needed
                            "last_df_name": last_df_name
                        }
                except Exception as e:
                    return {
                        "output": None,
                        "error": str(e),
                        "result_df": None,
                        "all_dataframes": {},
                        "last_df_name":None
                    }
                finally:
                    # Reset stdout and pandas options
                    sys.stdout = old_stdout
                    pd.reset_option('display.max_rows')
                    pd.reset_option('display.max_columns')
                    pd.reset_option('display.width')
                    pd.reset_option('display.max_colwidth')

            result = execute_python(state['code'], data)
            # return {"result": result}
            # Initialize retry count if not present
            retry_count = state.get("retry_count", 0)
            # st.write(f"This type of result: {type(result['output'])}")
            
            error = result.get("error", None)
            if error:
                # retry_count=1
                st.write(f"Got erorr, Number of retries : {retry_count + 1}.")
                if retry_count < 3:
                    retry_count += 1
                    goto_agent = "generate_code"  # Retry code generation
                else:
                    goto_agent = END
                    st.write("Max retries reached. Stopping.")
            else:
                goto_agent = "summarize_result"

      
            return Command(
                    update={"result": result,
                            "out_df": result['result_df'],
                            "last_df_name":result['last_df_name'],
                            "retry_count": retry_count,
                            },          
                    goto= goto_agent
                )

        def summarize_result(state: MessageState) -> Command[Literal[ "__end__"]]:
            """Summarize the result of the code execution to human understable language"""
            summarize_prompt = f"""Write the answer to the query from the output and ONLY IF REQUIRED to anser take help of DATA
                                - The audience is experts in lifesciences and healthcare sector
                                - The answer must provide clarity
                                - Query: {state['messages'][-1]}
                                - Output: {state['result']['output']}
                                - Data: {state['out_df']}
                                """

            llm = ChatOpenAI(model="gpt-4o",  max_tokens=None)

            messages = [
                (
                    "system",
                    "You are a good at answering and summarizing results. Summarize results of data based on the user's query.",
                ),
                ("human", summarize_prompt),
            ]

            summary = llm.invoke(messages)
            summary_text = summary.content
            
            return Command(
                update={"summary": summary_text},
                goto= END,
            )

        # Build and run the graph
        builder = StateGraph(MessageState)
        builder.add_edge(START, "select_dataframe")
        builder.add_node("select_dataframe", select_dataframe)
        builder.add_node("generate_code", generate_code)
        builder.add_node("agent", agent)
        builder.add_node("summarize_result", summarize_result)
        graph = builder.compile()

        # Invoke the graph
        answer = graph.invoke({
                    "messages": [HumanMessage(content=prompt)],
                    "code": "",
                    "result": {},
                    "retry_count": 0,  # Initialize retry count
                    "next": "",  # Define the next step (empty for now)
                    "dfs": [],  # Initialize as an empty list
                    "out_df": None, # Initialize out_df to None or an empty DataFrame
                    "summary": "",
                    "last_df_name":"",  
                })

        # Display assistant response
        # response = answer['result']['output'] if answer['result'].get('output') else f"Error: {answer['result']['output'].get('error')}"
        # response = answer['result']
        response = answer['summary'] if answer['summary']!="" else f"Error: {answer['result']['output'].get('error')}"
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display assistant response
        with st.chat_message("assistant"):
            # Always show generated code
            # st.code(answer.get('code', ''), language='python')
            with st.expander("View Code"):
                df_placeholder = st.empty()
                full_code= answer.get('code', '')
                df_placeholder.code(full_code, language= "python")

            with st.expander(f"Showing the Dataframe:{answer['last_df_name']}"):
                code_placeholder = st.empty()
                full_df= answer.get('out_df', '')
                code_placeholder.dataframe(full_df)
                
            # Handle execution results
            if answer['result'].get('output'):
                # Preserve whitespace formatting using a code block
                st.write(response)
            elif answer['result'].get('error'):
                st.error(f"Error: {answer['result']['error']}")
            
            # Update chat history with formatted output
            # formatted_response = f"```text\n{answer['result'].get('output', '')}\n```" if answer['result'].get('output') else f"Error: {answer['result'].get('error')}"
            # st.session_state.messages.append({"role": "assistant", "content": formatted_response})
