class MailUtils:
    @staticmethod
    def parts_has_attachments(parts):
        """
        check whether the parts have an attachment
        :param parts: check for attachments in there
        :return:
        """
        for part in parts:
            filename = part.get("filename")
            body = part.get("body", {})
            att_id = body.get("attachmentId")
            if filename and att_id:
                return True
        return False
