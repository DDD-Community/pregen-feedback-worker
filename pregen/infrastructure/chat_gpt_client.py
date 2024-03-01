from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from pregen.pojo.response.word_error_response import WordErrorResponse
from pregen.utils.environment import get_envs
from pregen.utils.singleton import singleton


@singleton
class ChatGptClient:
    def __init__(self):
        template_path = get_envs().openai["template_path"]

        with open(template_path, "r") as template_file:
            self.template = template_file.read()

        self.parser = PydanticOutputParser(pydantic_object=WordErrorResponse)
        self.prompt = PromptTemplate(
            template=self.template,
            input_variables=["original_script", "spoken_script"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.model = ChatOpenAI(
            api_key=get_envs().openai["api_key"], temperature=0
        )

        self.chain = self.prompt | self.model | self.parser

    def call(self, original_script: str, spoken_script: str) -> WordErrorResponse:
        return self.chain.invoke(
            {"original_script": original_script, "spoken_script": spoken_script}
        )
