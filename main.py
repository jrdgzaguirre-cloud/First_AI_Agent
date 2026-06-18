import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    #parse command-line arguments
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    #create a list of messages to send to the model, with the user's prompt as the input
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    #load environment variables from a .env file
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
    client = genai.Client(api_key=api_key)
    for _ in range(20):
        #generate a response from the model using the user's prompt
        response = client.models.generate_content(
            model='gemini-2.5-flash', contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )

        #make model aware of messages history
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        if not response.usage_metadata:
            raise RuntimeError("No usage metadata returned in the response.")
        if response.function_calls:
            function_results = []
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, args.verbose)
                if not function_call_result.parts:
                    raise Exception('Error: types.Content object has empty .parts attribute')
                if not function_call_result.parts[0].function_response:
                    raise Exception('Error:  types.Content object has no .function_response attribute')
                if not function_call_result.parts[0].function_response.response:
                    raise Exception('Error: FunctionResponse object has no .response attribute')
                function_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            #make model aware of messages history
            messages.append(types.Content(role="user", parts=function_results))
        else:
            print("Agent final response:", response.text)
            break
    else:
        print("Error: Agent reached max iterations without final response")


if __name__ == "__main__":
    main()