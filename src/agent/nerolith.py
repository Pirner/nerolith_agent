import base64
from pprint import pprint

import transformers
import torch

from src.MailAccess.utils import MailUtils


class Nerolith:
    """
    main class for the agent.
    This agent is responsible to execute each individual action and read the context plus triggering the model.
    """
    def __init__(self):
        # self.model_id = "C:/dev/repos/bismarck/meta-llama/Meta-Llama-3-8B-Instruct"
        self.model_id = "C:/dev/repos/bismarck/meta-llama/Meta-Llama-3.2-1B-Instruct"

        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )

        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    def get_text_from_parts(self, parts):
        """Recursively extract plain text from email parts"""
        for part in parts:
            if part.get("parts"):
                # If this part has nested parts, recurse into them
                return self.get_text_from_parts(part["parts"])
            mime_type = part.get("mimeType")
            if mime_type == "text/plain":
                data = part["body"].get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8")
                    return decoded
        return None

    def _create_title(self, subject, email_text):
        system_prompt = \
            f"""
                    You are a bot that provides a title for an articel, nothing else. Just a simple title
                    """

        task = \
            f"""
                    Given am email with subject: {subject}

                    and the text inside: {email_text}
                    create a title for the information above, the title should be used for a filename.
                    """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Task: {task}"""}
        ]

        outputs = self.pipeline(
            # prompt,
            messages,
            max_new_tokens=1024,
            eos_token_id=self.terminators,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
        )
        # pprint(email_text)
        title = outputs[0]["generated_text"][-1]['content']
        return title

    def _create_wiki_entry(
            self,
            subject,
            email_text,
    ):
        system_prompt = \
            f"""
            You are a bot that summarizes the content of an email and produce a wiki entry in markdown format.
            Make sure to write perfect markdown, nothing else.
            """

        task = \
            f"""
            Given am email with subject: {subject}

            and the text inside: {email_text}
            Write a summary of this email as an article with detailed information and produce perfect markdown, nothing
            else.
            The email had no attachment.
            """


        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Task: {task}"""}
        ]

        outputs = self.pipeline(
            # prompt,
            messages,
            max_new_tokens=1024,
            eos_token_id=self.terminators,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
        )
        # pprint(email_text)
        wiki_entry = outputs[0]["generated_text"][-1]['content']
        pprint(outputs[0]["generated_text"][-1]['content'])
        wiki_title = self._create_title(subject, email_text)
        with open('{}_wiki.md'.format(wiki_title), 'w') as f:
            f.write(wiki_entry)
        print('[INFO] created wiki entry')

    def _trigger_action(
            self,
            subject,
            email_text,
            has_attachments,
            parts,
    ):
        """
        trigger the action of the agent with all the emails processed.
        :param subject: the subject of the email to perform an action from
        :param email_text: text of the email that part of the email
        :param has_attachments: whether attachments are part of it or not
        :param parts: all the parts of the email
        :return:
        """
        system_prompt = f"""
        You are a bot that only provides an action given an email, nothing else.
        Provide exactly one function from the action list below, nothing else. name only the action NAME.
        Derive which action to chose from the email itself.
        Action list:
        name: create_todo description: create a task entry based on the content
        name: create_wiki_entry description: create an information entry based on the content of the email
        name: store_attachment description: store the attached file in a folder with a reason
        """
        system_prompt = \
        """
        You are an astute INTENT CLASSIFIER: given any piece of text
        from the user, you are able to smartly infer their intent.
        Given such a piece of text, classify its intent into one of the following:
        - create_todo
        - create_wiki_entry
        - store_attachment
        only reply with the exact option from the list.
        """

        task = f"""
        Given am email with subject: {subject}
        
        classify the intention based on the subject of the email.
        The email had no attachment.
        """
        # and the text inside: {email_text}

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Task: {task}"""}
        ]

        outputs = self.pipeline(
            # prompt,
            messages,
            max_new_tokens=128,
            eos_token_id=self.terminators,
            do_sample=True,
            temperature=0.05,
            top_p=0.9,
        )
        # print(outputs)
        pprint(outputs[0]["generated_text"][-1])

        action = outputs[0]["generated_text"][-1]['content']
        if action == 'create_todo':
            raise NotImplementedError('create todo not implemented')
        elif 'create_wiki' in action:
            self._create_wiki_entry(subject, email_text)
        elif action == 'store_attachment':
            raise NotImplementedError('save attachment not implemented.')
        else:
            raise Exception('did not find action for: ', action)

    def process_message(self, message):
        """
        process an email message
        :param message: the message to process in the agent
        :return:
        """
        parts = message['payload'].get('parts', [])

        # Get message headers
        headers = message.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        # print(f"Subject: {subject}")
        # Extract and print plain text
        email_text = self.get_text_from_parts(parts) or "(No plain text found)"
        # print("Body:", email_text)
        has_attachments = MailUtils.parts_has_attachments(parts=parts)

        self._trigger_action(
            subject=subject,
            email_text=email_text,
            has_attachments=has_attachments,
            parts=parts,
        )
