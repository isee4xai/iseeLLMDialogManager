from string import Template
import json
import re
import json
from collections import OrderedDict

from openai import OpenAI
import os
from pinecone import Pinecone, ServerlessSpec
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from uuid import uuid4

from business.bt.base_llm import *


API_KEY = os.environ['OPENAI_API_KEY'] 
# Set API key as an environment variable
os.environ["OPENAI_API_KEY"] = API_KEY
os.environ["HELICONE_API_KEY"] = os.environ['HELICONE_API_KEY']

# Directly when initializing the client for double assurance
client = OpenAI(
    api_key=API_KEY,
    base_url="https://oai.hconeai.com/v1", 
    default_headers={
        "Helicone-Auth": f"Bearer {os.environ['HELICONE_API_KEY']}"
    }
)

# Load environment variables or set your API keys directly
OPENAI_API_KEY = os.environ['OPENAI_API_KEY'] 
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
PINECONE_ENV = os.environ['PINECONE_REGION']

# Initialize OpenAI Embeddings
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai_embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# Initialize Pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to Pinecone index
index_name = "explainers-index"
if index_name not in [index_info["name"] for index_info in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embedding dimension
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    )
    print(f"Index '{index_name}' created successfully.")

# Wait until the index is ready
while not pc.describe_index(index_name).status["ready"]:
    print("Waiting for index to be ready...")
    time.sleep(1)

# Get the index
index = pc.Index(index_name)

# Initialize the updated Pinecone vector store with required parameters
vector_store = PineconeVectorStore(
    index=index,
    embedding=openai_embeddings,
    text_key="page_content",  # Key in Document schema to use as text content
)

print("Pinecone vector store initialized.")

def identify_dataset_and_explainers(input_text: str, openai_model) -> Tuple[List[str], List[str]]:
    """
    Identifies the types of datasets and explainers being discussed in the input text using the OpenAI model.
    Returns a tuple containing a list of dataset types and a list of explainer names.
    """
    prompt = f"""
Given the following text:

{input_text}

Identify the types of datasets being discussed (e.g., 'Multivariate tabular', 'Multivariate time series', 'Univariate time series', 'Image', 'Text', etc.), and list the names of explainers mentioned.

Provide the output in the following JSON format:

{{
    "DatasetTypes": ["dataset_type_1", "dataset_type_2", ...],
    "Explainers": ["explainer_name_1", "explainer_name_2", ...]
}}

Your response:
"""
    response_text = openai_model.inference_with_json(prompt)
    # Parse the response as JSON
    try:
        response_json = json.loads(response_text.choices[0].message.content)
        dataset_types = response_json.get("DatasetTypes", [])
        explainers_list = response_json.get("Explainers", [])
        # Clean up whitespace
        dataset_types = [dt.strip() for dt in dataset_types]
        explainers_list = [ex.strip() for ex in explainers_list]
        return dataset_types, explainers_list
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print("Response was:", response_text)
        return [], []

def query_explainers(dataset_types: List[str], explainers_list: List[str], k_per_type: int = 5) -> Dict[str, List[Document]]:
    """
    Queries the vector store to retrieve relevant explainers based on the dataset types and explainer names.
    Returns a dictionary mapping keys (dataset types and explainer names) to lists of Documents.
    """
    explainers_per_key = {}
    # Query based on dataset types
    for dt in dataset_types:
        # Build a filter for the dataset type
        filter = {
            "dataset_type": dt
        }
        results = vector_store.similarity_search(
            query=dt,
            k=k_per_type,
            filter=filter
        )
        explainers_per_key[dt] = results

    # Query based on explainer names without filtering
    for explainer_name in explainers_list:
        results = vector_store.similarity_search(
            query=explainer_name,
            k=k_per_type
            # No filter here, as per your request
        )
        explainers_per_key[explainer_name] = results

    return explainers_per_key

def refine_response(input_text: str, explainers_per_key: Dict[str, List[Document]], openai_model) -> str:
    """
    Refines the response using the retrieved explainers and the OpenAI model.
    """
    explainer_descriptions = ""
    for key, explainers in explainers_per_key.items():
        explainer_descriptions += f"\nFor '{key}' (found {len(explainers)} explainers):\n"
        explainer_descriptions += str(explainers)
        explainer_descriptions += "\n"

    prompt = f"""
Our current response is provided below:

{input_text}

Based on this, we have identified internal explainers relevant within our system:

{explainer_descriptions}

Provide a refined explanation, substituting the internal explainer information where appropriate. 
To identify when it is appropriate: consider if its an expansion on an explainer, or an explanation on several explainers. If so substitute.
If it is a genral text no need to substitute at all.If talks about task functionality or other non-explainer user query responses dont subtitute.
If the same explainer is present internally, mention the explainer name (e.g., '/Tabular/LIME') in the description.
Preserve the same current i.e if the current response is HTML.
Reference that the Isee Platform (our system) has such explainers and the user can try them out, Only if ti srlevant to add the explainer or refine. If no refinement is needed dont apply this or mention this.
If no explainers are there for ISee, don't explicitly mention it, because we may have missed it
Essentially, the response is for a user query, and if the user is curious about other explanations or explainers, we can promote existing ones in our system.
Return Your output enclosed in Valid HTML tags. Enclose your output output with a <div> </div>. Start like this and I need to embed the output inside a html container. The HTML output is very important.
"""
    response_text = openai_model.inference(prompt)
    return response_text.choices[0].message.content




def post_process_input_text(input_text: str) -> str:
    """
    Processes the input text to identify dataset types, retrieve explainers, and refine the response.
    """
    openai_model = GPT_4o_post_processor_model

    # Step 1: Identify dataset types and explainers
    dataset_types, explainers_list = identify_dataset_and_explainers(input_text, openai_model)
    print(f"Identified dataset types: {dataset_types}")
    print(f"Identified explainers: {explainers_list}")

    if not dataset_types and not explainers_list:
        print("No dataset types or explainers identified.")
        return input_text

    # Step 2: Query explainers from vector store
    explainers_per_key = query_explainers(dataset_types, explainers_list, k_per_type=5)

    total_explainers = sum(len(explainers) for explainers in explainers_per_key.values())
    print(f"Retrieved {total_explainers} explainers.")

    for key, explainers in explainers_per_key.items():
        print(f"Found {len(explainers)} explainers for key '{key}'")

    # Step 3: Refine response
    if len(explainers_list) > 0:
        refined_response = refine_response(input_text, explainers_per_key, openai_model)
        return refined_response
    else:
        return input_text


class GPT4o_Model(OpenAI_Model):
    """
    GPT-4o Model class extending the OpenAI_Model class.
    Utilizes the OpenAI client call method for API interaction.
    Inherits from OpenAI_Model and overrides the inference method for GPT-4 specific usage.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GPT4o_Model with the configuration dictionary.
        Uses OpenAI client for API interaction with additional API settings.

        :param config: Configuration dictionary for the model.
        """
        # Set up default model and API key details, and initialize the client
        self.model = config.get("model", "gpt-4")
        api_key = config.get("api_key", os.getenv("OPENAI_API_KEY"))
        helicone_key = os.getenv("HELICONE_API_KEY")

        # If no API key is provided in config or environment, raise an error
        if not api_key:
            raise ValueError("API key is required for GPT-4 model initialization.")

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://oai.hconeai.com/v1",
            default_headers={"Helicone-Auth": f"Bearer {helicone_key}"}
        )

        self.temperature = config.get("temperature", 1.0)
        self.max_tokens = config.get("max_tokens", None)
        self.n = config.get("n", 1)
        self.stop = config.get("stop", None)
        self.frequency_penalty = config.get("frequency_penalty", 0.0)
        self.presence_penalty = config.get("presence_penalty", 0.0)

        super().__init__(config)

    def _validate_config(self) -> None:
        """
        Override config validation for GPT-4o Model to check client initialization and parameters.
        Ensures required keys are present and valid client initialization.

        :raises ValueError: If required keys or configurations are invalid.
        """
        required_keys = ["model"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

        # Validate temperature
        if not (0 <= self.temperature <= 2):
            raise ValueError("Temperature must be between 0 and 2.")

        # Validate frequency penalty
        if not (-2 <= self.frequency_penalty <= 2):
            raise ValueError("Frequency penalty must be between -2 and 2.")

        # Validate presence penalty
        if not (-2 <= self.presence_penalty <= 2):
            raise ValueError("Presence penalty must be between -2 and 2.")

        # Validate max_tokens only if provided
        if self.max_tokens is not None and not (0 <= self.max_tokens <= 4096):
            raise ValueError("Max tokens must be between 0 and 4096 for GPT-4.")

    def generate_api_request(self, prompt_text: str, images_dict: Dict[str, str], max_tokens: Optional[int] = None) -> str:
        """
        Function to call the GPT-4o API with a prompt and associated images in base64 format.

        :param prompt_text: The input text prompt for the model.
        :param images_dict: A dictionary where keys are image numbers and values are base64-encoded images.
        :param max_tokens: Optional maximum number of tokens for the response. Only included if provided.
        :return: The generated text from the GPT-4 API.
        """
        # Construct message content with the prompt and base64-encoded images
        message_content = [{"type": "text", "text": prompt_text}]
        for image_num, base64_image in images_dict.items():
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        # API call to the OpenAI GPT-4 model
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            # Only pass max_tokens if provided
            **({"max_tokens": max_tokens} if max_tokens else {})
        )

        # Return the generated text response
        return response

    def generate_api_request_with_json(self, prompt_text: str, images_dict: Dict[str, str], max_tokens: Optional[int] = None) -> str:
        """
        Function to call the GPT-4o API with a prompt and associated images in base64 format.

        :param prompt_text: The input text prompt for the model.
        :param images_dict: A dictionary where keys are image numbers and values are base64-encoded images.
        :param max_tokens: Optional maximum number of tokens for the response. Only included if provided.
        :return: The generated text from the GPT-4 API.
        """
        # Construct message content with the prompt and base64-encoded images
        message_content = [{"type": "text", "text": prompt_text}]
        for image_num, base64_image in images_dict.items():
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        # API call to the OpenAI GPT-4 model
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            # Only pass max_tokens if provided
            **({"max_tokens": max_tokens} if max_tokens else {}),
            response_format = {"type": "json_object"}
        )

        # Return the generated text response
        return response

    def inference(self, prompt_text: str, images_dict: Dict[str, str] = {}, args: Dict[str, Any] = {}) -> str:
        """
        Perform inference using the GPT-4 model via the OpenAI client call method.

        :param prompt_text: The input text prompt for the model.
        :param images_dict: Dictionary where keys are image numbers and values are base64-encoded image data.
        :param args: Additional arguments, including max_tokens, temperature, etc.
        :return: The generated text response from the GPT-4 API.
        """
        max_tokens = args.get("max_tokens", None)  # Optional max_tokens argument

        # Generate the API request using the prompt and images
        return self.generate_api_request(prompt_text, images_dict, max_tokens)

    def inference_with_json(self, prompt_text: str, images_dict: Dict[str, str] = {}, args: Dict[str, Any] = {}) -> str:
        """
        Perform inference using the GPT-4 model via the OpenAI client call method.

        :param prompt_text: The input text prompt for the model.
        :param images_dict: Dictionary where keys are image numbers and values are base64-encoded image data.
        :param args: Additional arguments, including max_tokens, temperature, etc.
        :return: The generated text response from the GPT-4 API.
        """
        max_tokens = args.get("max_tokens", None)  # Optional max_tokens argument

        # Generate the API request using the prompt and images
        return self.generate_api_request_with_json(prompt_text, images_dict, max_tokens)

GPT_4o_CONFIG = {
    "model": "gpt-4o-2024-08-06",
    "api_key": os.environ["OPENAI_API_KEY"],
    "temperature": 0.0,
}
GPT_4o_model = GPT4o_Model(GPT_4o_CONFIG)

# Function to extract images only
def extract_images_only(json_data):
    """Extracts and returns images from the JSON data."""
    # Parse the JSON data
    data = json.loads(json_data) if type(json_data) != dict else json_data
    executions = data.get('executions', [])
    image_references = {}
    image_counter = 1

    for execution in executions:
        node_exec = execution.get("http://www.w3.org/ns/prov#generated", {})
        if "https://www.w3id.org/iSeeOnto/BehaviourTree#properties" in node_exec:
            exec_properties = node_exec["https://www.w3id.org/iSeeOnto/BehaviourTree#properties"]
            for exec_prop in exec_properties.get("https://www.w3id.org/iSeeOnto/BehaviourTree#hasDictionaryMember", []):
                exec_value = exec_prop.get('https://www.w3id.org/iSeeOnto/BehaviourTree#pair_value_object')
                if isinstance(exec_value, dict) and 'content' in exec_value and 'src="data:image' in exec_value['content']:
                    start_index = exec_value['content'].find('src="data:image')
                    end_index = exec_value['content'].find('"', start_index + 5)
                    image_data = exec_value['content'][start_index + 5:end_index]
                    image_references[image_counter] = image_data
                    image_counter += 1
    return image_references

def extract_node_properties_and_images(json_data):
    # Parse the JSON data
    data = json.loads(json_data) if type(json_data) != dict else json_data
    
    # Extract the executions
    executions = data.get('executions', [])
    
    # Dictionary to store image references
    image_references = {}
    image_counter = 1
    
    # List to store node properties as text in order of execution
    node_properties_text = []
    
    # List to store explanations given
    explanations_given = []
    
    for execution in executions:
        node_instance = execution.get('https://www.w3id.org/iSeeOnto/BehaviourTreeExecution#enacted', {}).get('instance')
        node_properties = None
        
        for node in data.get('nodes', []):
            if node.get('instance') == node_instance:
                node_properties = node.get('https://www.w3id.org/iSeeOnto/BehaviourTree#properties', {}).get('https://www.w3id.org/iSeeOnto/BehaviourTree#hasDictionaryMember', [])
                break
        
        if node_properties:
            properties_text = f"Node Instance: {node_instance}\n"
            for prop in node_properties:
                key = prop.get('https://www.w3id.org/iSeeOnto/BehaviourTree#pairKey')
                value = prop.get('https://www.w3id.org/iSeeOnto/BehaviourTree#pair_value_object')
                
                properties_text += f"  {key}: {value}\n"
                
                # Check if the key is 'question' to extract explanations
                if key == 'question':
                    explanations_given.append(value)
            
            # Add execution content
            node_exec = execution.get("http://www.w3.org/ns/prov#generated", {})
            if "https://www.w3id.org/iSeeOnto/BehaviourTree#properties" in node_exec:
                exec_properties = node_exec["https://www.w3id.org/iSeeOnto/BehaviourTree#properties"]
                exec_properties_text = "  Execution Properties:\n"
                for exec_prop in exec_properties.get("https://www.w3id.org/iSeeOnto/BehaviourTree#hasDictionaryMember", []):
                    exec_key = exec_prop.get('https://www.w3id.org/iSeeOnto/BehaviourTree#pairKey')
                    exec_value = exec_prop.get('https://www.w3id.org/iSeeOnto/BehaviourTree#pair_value_object')
                    
                    # Check if the value is an image
                    if isinstance(exec_value.get("content"), str) and 'src="data:image' in exec_value:
                        # Extract the base64 image data from the src attribute
                        start_index = exec_value.find('src="data:image')
                        end_index = exec_value.find('"', start_index + 5)
                        image_data = exec_value[start_index + 5:end_index]
                        image_placeholder = f"image[{image_counter}]"
                        image_references[image_counter] = image_data
                        exec_properties_text += f"    {exec_key}: {image_placeholder}\n"
                        image_counter += 1
                    else:
                        exec_properties_text += f"    {exec_key}: {exec_value}\n"
                
                properties_text += exec_properties_text
            
            node_properties_text.append(properties_text)
    
    return "\n".join(node_properties_text), image_references, explanations_given

# Function to extract base64 data from image URLs
def extract_base64_data(data_url):
    base64_pattern = r'^data:image/[a-zA-Z]+;base64,(.+)$'
    match = re.match(base64_pattern, data_url)
    if match:
        return match.group(1)
    else:
        return None

import re
import markdown

def clean_and_convert_to_html(content: str) -> str:
    """
    Cleans the input content by removing code fences or markers (e.g., ```html, ```markdown, ```whatever)
    from the beginning and end of the string. Detects if the content is Markdown or HTML, and converts
    Markdown content to HTML.

    Args:
        content (str): The input string containing code fences and either Markdown or HTML content.

    Returns:
        str: The cleaned content as HTML.

    Examples:
        >>> markdown_content = '''```markdown
        ... # Header
        ... This is a *Markdown* example.
        ... ```'''
        >>> clean_and_convert_to_html(markdown_content)
        '<h1>Header</h1>\\n<p>This is a <em>Markdown</em> example.</p>'

        >>> html_content = '''```html
        ... <p>This is valid HTML content.</p>
        ... ```'''
        >>> clean_and_convert_to_html(html_content)
        '<p>This is valid HTML content.</p>'
    """
    # Strip leading and trailing whitespace
    content = content.strip()

    # Remove starting code fence and any language specifier
    content = re.sub(r'^```[\w\s]*\n', '', content)

    # Remove ending code fence
    content = re.sub(r'\n```$', '', content)

    # Strip again in case there was whitespace after removing code fences
    cleaned_content = content.strip()

    # Check if the content contains HTML tags
    def contains_html_tags(text: str) -> bool:
        """
        Checks if the text contains HTML tags.

        Args:
            text (str): The text to check.

        Returns:
            bool: True if HTML tags are found, False otherwise.
        """
        html_tag_pattern = re.compile(r'<[^>]+>')
        return bool(html_tag_pattern.search(text))

    if contains_html_tags(cleaned_content):
        # Assume it's already valid HTML
        return cleaned_content
    else:
        # Convert Markdown to HTML
        return markdown.markdown(cleaned_content)


# Function to extract node properties, images, and explanations
def extract_rich_properties(json_data):
    # Get node properties text and explanations
    node_properties_text, _, explanations_given = extract_node_properties_and_images(json_data)
    # Get image references and their base64 data
    image_references = extract_images_only(json_data)
    image_data_references = {k: extract_base64_data(v) for k,v in image_references.items()}
    explanations_given = [x for x in explanations_given if x != "None"]

    image_ref_names = {}
    for idx, ref in enumerate(list(image_references.keys())):
        image_ref_names[idx + 1] = ([f"<Image-{idx + 1}-URL>", f"<Image-{idx + 1}-Base_Data>"])
        image_url = image_references[ref]
        image_base_data = image_data_references[ref]
        node_properties_text = node_properties_text.replace(image_url, f"<Image-{idx + 1}-URL>").replace(image_base_data, f"<Image-{idx + 1}-Base_Data>")

    return node_properties_text, explanations_given, image_references, image_data_references, image_ref_names

# Convert image references to text
def convert_image_references_to_text(image_references):
    text_output = []
    for idx, (image_number, references) in enumerate(image_references.items(), start=1):
        url, base64_data = references
        text = f"The {ordinal(idx)} image URL is referenced by this: {url}, and its base64 encoded data is referenced like this: {base64_data}."
        text_output.append(text)
    return " ".join(text_output)

# Helper function to convert number to ordinal
def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

# Convert chat history to text
def convert_chat_history_to_text(chat_history):
    formatted_history = []
    for entry in chat_history:
        if "user" in entry:
            formatted_history.append(f"User: {entry['user']}")
        elif "system" in entry:
            formatted_history.append(f"System: {entry['system']}")
    return "\n".join(formatted_history) if len(chat_history) != 0 else "[]"

# Template for the prompt
def generate_prompt(behavior_tree_history, user_question, image_references_text, explanation_focus, chat_history):
    template = Template("""
References for images used in the behavior tree history and variable details are below:
$image_references
The images will be uploaded separately. Please analyze them thoroughly and utilize the knowledge for later.

Given this behavior tree history of the chatbot:
$behavior_tree_history

Focus on these areas of the node which are in order of execution:
$explanation_focus

For the latest explanation given by the system:
The user chat history and your responses are below(you are referenced as the 'system'):
$chat_history

The user's current question:

<user>: $user_question

When answering the question, don’t reference the behavior tree or the user chat history directly (dotn say sytem said this likeiwse it as to be natural) or dont mention yourself or yourself as the system. Just answer the user’s question as it references the latest explanation we provided.
In your reference dont reoeat teh suer chat histroy ever. Dont say according to the chat history. Just answer the question as QA Assistant.
Use the chat history for the explanation as guided context to understand what position the user is in in understanding the system.
You can use the history to elaborate on certain points or make references to improve your current answer.
If the context dont have an image, dont say that you are unable to analyze or provide details about the image. Address the query without it.
Return Your output enclosed in Valid HTML tags. Enclose your output output with a <div> </div>. Start like this and I need to embed the output inside a html container. The HTML output is very important.
""")
    return template.substitute(
        behavior_tree_history=behavior_tree_history,
        user_question=user_question,
        image_references=image_references_text,
        explanation_focus=explanation_focus,
        chat_history=chat_history
    )

# Function to handle the entire pipeline
def full_pipeline(json_history, chat_history, user_question):
    # Extract rich properties from JSON history
    node_properties_text, explanations_given, image_references, image_data_references, image_ref_names = extract_rich_properties(json_history)
    
    # Convert image references and chat history to text
    image_references_text = convert_image_references_to_text(image_ref_names)
    chat_history_text = convert_chat_history_to_text(chat_history)
    
    # Generate the final prompt
    prompt = generate_prompt(node_properties_text, user_question, image_references_text, explanations_given, chat_history_text)

    # Return the prompt and image data references to send
    return prompt, image_data_references, image_ref_names

# Function to call the LLM API with the prompt and images
def generate_api_request(model, prompt_text, images_dict):
    return GPT_4o_model.inference(prompt_text, images_dict)
    # message_content = [{"type": "text", "text": prompt_text}]
    # for image_num, base64_image in images_dict.items():
    #     message_content.append({
    #         "type": "image_url",
    #         "image_url": {
    #             "url": f"data:image/jpeg;base64,{base64_image}"
    #         },
    #     })
    # response = client.chat.completions.create(
    #     model=model,
    #     temperature=0,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": message_content,
    #         }
    #     ],
    #     max_tokens=500,
    # )
    # return response

from collections import defaultdict

# Function to group and track order of clarification nodes
def process_executions_with_order(data):
    executions = data.get("executions", [])
    node_history = defaultdict(list)  # Dictionary to store history for each node_id
    latest_node_entry = {}  # Store the latest entry for each node_id
    node_order = []  # List to keep track of clarification node order

    # Iterate through each execution in the list
    for index, exec_data in enumerate(executions):
        clr_exec = exec_data.get("CLR_EXEC", {}).get("<CLR_EXEC>", [])
        
        # Find the clarification_node_id in this execution group
        clarification_node_id = next(
            (item['clarification_node_id'] for item in clr_exec if 'clarification_node_id' in item), None)

        if clarification_node_id:
            # Append the entire execution group to the node's history
            node_history[clarification_node_id].append(exec_data)
            
            # Update the latest node group and entry (assuming the most recent one is the last)
            latest_node_entry[clarification_node_id] = {
                "clarification_question": next((item['clarification_question'] for item in clr_exec if 'clarification_question' in item), None),
                "llm_response": next((item['llm_response'] for item in clr_exec if 'llm_response' in item), None),
                "llm_history": next((item['llm_history'] for item in clr_exec if 'llm_history' in item), None),
                "clarification_node_id": clarification_node_id
            }
            
            # Add the clarification node and its position in the order
            node_order.append({
                "clarification_node_id": clarification_node_id,
                "execution_order": index + 1  # Tracking the execution order (1-based)
            })

    # Now get the last node based on order
    if node_order:
        last_node_id = node_order[-1]['clarification_node_id']  # Last node in the order
        last_node_history = node_history[last_node_id]  # Get all execution data for the last node

        # Create the final dictionary with latest node group, latest node, full node history, and order
        result = {
            "last_node_id": last_node_id,
            "last_node_history": last_node_history,  # All executions for the last node
            "latest_node_entry": latest_node_entry,  # Latest entry by node_id
            "full_node_history": node_history,       # Full history by node_id
            "node_order": node_order                 # Order of clarification nodes in executions
        }
    else:
        result = {
            "last_node_id": None,
            "last_node_history": [],
            "latest_node_entry": latest_node_entry,
            "full_node_history": node_history,
            "node_order": node_order
        }

    # Iterate through each execution in the list
    last_node_group = []
    for index, exec_data in enumerate(executions):
        clr_exec = exec_data.get("CLR_EXEC", {}).get("<CLR_EXEC>", [])
        
        # Find the clarification_node_id in this execution group
        clarification_node_id = next(
            (item['clarification_node_id'] for item in clr_exec if 'clarification_node_id' in item), None)

        if clarification_node_id:
            # Group chat history of last explainer
            if clarification_node_id == last_node_id:
                last_node_group.append(exec_data)

    result["latest_node_group"] = last_node_group
    return result

from string import Template

# Template for the overall clarification history
clarification_template = Template("""
Clarification Node:
$clarification_node

Clarification History:
$user_conversation
""")

# Template for each user and assistant conversation
conversation_template = Template("""
<user>: $user_question
<assistant>: $llm_response
""")

# Function to generate clarification conversation history
from string import Template

# Template for the overall clarification history
clarification_template = Template("""
Clarification Node:
$clarification_node

Clarification History:
$user_conversation
""")

# Template for each user and assistant conversation
conversation_template = Template("""
<user>: $user_question
<assistant>: $llm_response
""")

# Function to generate clarification conversation history
def generate_clarification_history(latest_clarification_group):
    clarification_node = "Unknown Node"
    conversation_history = ""

    # Loop through each entry in the clarification group (assuming it's a list)
    for entry in latest_clarification_group:
        # Directly access the clarification details from CLR_EXEC
        if 'CLR_EXEC' in entry:
            clarification = entry['CLR_EXEC']['<CLR_EXEC>']  # Access the list directly

            # print(clarification[0])
            # Extract clarification details
            clarification_question = clarification[0].get('clarification_question', {})
            llm_response = clarification[1].get('llm_response', 'No Response')
            clarification_node = clarification[3].get('clarification_node_id', clarification_node)
            
            # Build the conversation history using the template
            conversation_history += conversation_template.substitute(
                user_question=clarification_question,
                llm_response=llm_response
            )

    # Fill in the clarification history template
    clarification_history = clarification_template.substitute(
        clarification_node=clarification_node,
        user_conversation=conversation_history
    )

    return clarification_history
    
GPT_4o_CONFIG = {
    "model": "gpt-4o-2024-08-06",
    "api_key": os.environ["OPENAI_API_KEY"],
    "temperature": 0.0,
}
GPT_4o_post_processor_model = GPT4o_Model(GPT_4o_CONFIG)