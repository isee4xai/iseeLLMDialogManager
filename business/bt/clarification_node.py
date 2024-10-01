import re
import json
from datetime import datetime
import business.bt.nodes.node as node
import business.storage as s
from business.bt.nodes.type import State
from business.bt.llm_pipeline import *
from typing import List, Optional, Callable


class LLMClarificationQuestionNode(node.Node):
    """
    A node for asking the user if they understood the previous explanation
    and offering clarification if needed.
    """

    def __init__(self, id: str, variable: str = None, clarification_variable: str = None) -> None:
        super().__init__(id)
        self.question = "Did you understand the previous explanation?"
        self.clarification_question = "Would you like a different explanation or an elaboration on the existing one?"
        self.variable = variable or "clarification_response"
        self.clarification_variable = clarification_variable or "clarification_choice"
        
        # Add flag to mark this as a clarification node
        self.is_clarification_node = True
        # Dictionary to hold clarification-related data
        self.clarification_data = {}
        self.clarification_history = []

    def toString(self) -> str:
        return ("LLM CLARIFICATION QUESTION " + str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    def reinsert_image_to_message(self, message, image_dict):
        """
        Identifies all src attributes in the message, extracts numbers from their content,
        assigns numbers if none are present, and replaces the src content with corresponding
        base64 strings from image_dict based on the extracted or assigned numbers.

        Args:
        - message (str): The HTML content as a string.
        - image_dict (dict): A dictionary where keys are numbers (as strings) and values are base64 image strings.

        Returns:
        - str: The modified message with updated src attributes.
        """

        next_number = [1]  # Use a list to make 'next_number' mutable within nested function

        # Function to extract number from a string
        def extract_number(s):
            numbers = re.findall(r'\d+', s)
            if numbers[0] == '64':
                return int(numbers[1])
            return int(numbers[0]) if numbers else None

        # Function to replace src attributes in the message
        def replace_src(match):
            original_src = match.group(1)
            number = extract_number(original_src)
            print(match, number)

            # If no number found, assign the next available number
            if not number:
                number = int(next_number[0])
                next_number[0] += 1

            # Get the base64 image data from image_dict using the number
            if number in image_dict:
                base64_data = image_dict[number]

                # Determine the MIME type from the original src if possible
                mime_type_match = re.search(r'data:(image/\w+);base64', original_src)
                if mime_type_match:
                    mime_type = mime_type_match.group(1)
                else:
                    # Default MIME type
                    mime_type = 'image/png'

                # Create the new src content
                new_src = f'data:{mime_type};base64,{base64_data}'
                return f'src="{new_src}"'
            else:
                # If the number is not in image_dict, leave the src unchanged
                return match.group(0)

        # Regular expression to find all src attributes, matching both single and double quotes
        src_pattern = r'src=["\']([^"\']*)["\']'

        # Replace all src attributes in the message
        modified_message = re.sub(src_pattern, replace_src, message)

        return modified_message


    def generate_llm_response(self, chat_history, user_question) -> str:

        user_history = self.clarification_history
        # Generate prompt and images dictionary
        prompt, images_dict, image_ref_names = full_pipeline(chat_history, user_history, user_question)

        # Print or process the response
        print(user_history)
        # Save prompts, imade)dcit and calrifcation_shitry in a file
        with open('clarification_history.json', 'w') as f:
            json.dump(user_history, f)

        with open('clarification_prompt.json', 'w') as f:
            json.dump(prompt, f)

        with open('clarification_images.json', 'w') as f:
            json.dump(images_dict, f)


        try:
            response = GPT_4o_model.inference(prompt, images_dict)

            with open("llm_response.json", "w") as f:
                f.write(response.json())

            main_response = response.choices[0].message.content

            # Reinsert images to the response
            images_dict = {int(k): v for k, v in images_dict.items()}
            main_response = self.reinsert_image_to_message(main_response, images_dict)
            # store return response
            with open("llm_response_text.json", "w") as f:
                f.write(main_response)
            return main_response
        except Exception as e:

            with open("llm_response.json", "w") as f:
                f.write(f"Error: {e}")
            return "I am sorry, I am unable to generate a response at the moment. Please try again later."

    async def tick(self) -> State:
        self.start = datetime.now()
        print("I am in the LLM Clarification Question Node")
        # save json to file
        with open('chat_history.json', 'w') as f:
            json.dump(self.co.logger.json_history(), f)

        # Ask if the user understood the previous explanation
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [
            s.Response("yes", "Yes"),
            s.Response("partial", "Partially"),
            s.Response("no", "No")
        ]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        # Get the user's response
        response = json.loads(self.co.check_world(self.variable))

        if ("partial" in response["content"].lower()) or ("no" in response["content"].lower()):
            # Ask for clarification
            q = s.Question(self.id, self.clarification_question, s.ResponseType.OPEN.value, True)
            _clarification_question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_clarification_question, self.clarification_variable)
            
            clarification_response = json.loads(self.co.check_world(self.clarification_variable))
            print(f"Clarification Question Node Response {clarification_response}")
            
            # Send the LLM response message
            llm_message = self.generate_llm_response(self.co.logger.json_history(), clarification_response["content"])
            self.clarification_history.append({
                "user": clarification_response["content"],
                "system": llm_message
            })

            llm_question = s.Question(self.id, llm_message, s.ResponseType.INFO.value, False)
            llm_json = json.dumps(llm_question.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send(llm_json)

            self.status = State.FAILURE
        else:
            self.status = State.SUCCESS
            return self.status

        # Add clarification data to the node
        self.clarification_data = {
            "clarification_question": clarification_response["content"],
            "llm_response": llm_message, 
            "llm_history": "placeholder history",
            "clarification_node_id": self.id
        }

        # Log the interaction with the node data
        self.end = datetime.now()
        self.co.log(node=self, question=_clarification_question, variable=self.co.check_world(self.clarification_variable), **self.clarification_data)
        # save json to file
        with open('chat_history.json', 'w') as f:
            json.dump(self.co.logger.json_history(), f)

        return self.status



class RepeatUntilNode(node.Node):
    """
    A node that repeats execution of its children until a specified condition is met.
    
    :param id: The unique identifier for this node.
    :param repeat_condition: A function that takes a node status and returns True if repeating should continue.
                             Defaults to requiring all children to succeed.
    """

    def __init__(self, id: str, repeat_condition: Optional[Callable[[State], bool]] = None) -> None:
        super().__init__(id)
        self.children: Optional[List[node.Node]] = None
        self.repeat_condition = repeat_condition if repeat_condition != None else lambda x: self.default_repeat_condition(x)

    def toString(self) -> str:
        """
        Return a string representation of the node.

        :return: String representation of the node.
        """
        return ("REPEAT UNTIL " + str(self.status) + " " + str(self.id))

    def default_repeat_condition(self, status: State) -> bool:
        """
        Default repeat condition that requires all children to be in the SUCCESS state.

        :param status: The status of the node.
        :return: True if the condition to repeat is met, otherwise False.
        """
        return status != State.SUCCESS

    async def tick(self) -> State:
        """
        Execute the node's logic, repeating the execution of its children until the condition is met.

        :return: The status of the node after execution.
        """
        self.start = datetime.now()
        self.status = State.FAILURE

        if self.children is None or len(self.children) == 0:
            self.status = State.SUCCESS
        else:
            while self.repeat_condition(self.status):
                for child in self.children:
                    self.status = await child.tick()
                    print(f"Repeat Until Node Child Status {self.status}")
                    if not self.repeat_condition(self.status):
                        break

        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self) -> None:
        """
        Reset the node status to FAILURE and reset all its children.

        :return: None
        """
        self.status = State.FAILURE
        if self.children:
            for child in self.children:
                child.reset()

