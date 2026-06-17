



from utils.read_config import ReadConfig as rc


class Model:
    """

    """
    def __init__(self, log, genai):
        """

        """
        self.log = log
        self.genai = genai


    def analyze_code_gap(self, data, flag):
        """

        :param data:
        :param flag:
        :return:
        """
        self.log.info("Call gemini model for analyze changed code...")
        prompt = None

        if flag == "Azure":
            prompt = open(f"{rc.get_project_path()}/src/llm/prompts/azure_gap_analysis_prompt.txt", "r").read()
        elif flag == "GitHub":
            prompt = open(f"{rc.get_project_path()}/src/llm/prompts/github_gap_analysis_prompt.txt", "r").read()

        gemini = self.genai.Client(api_key= rc.gemini_api_key())
        for item in data.get("changed_files", []):
            response = gemini.models.generate_content(
                model= "gemini-3-flash-preview",
                contents= prompt.format(
                    FILE_PATH= item.get("path"),
                    CHANGED_CODE= item.get("code"))
            )
            item["report"] = self.extract_text(response= response)


    def extract_text(self, response):
        """
        Robust text extraction for Gemini multi-part responses.
        """
        self.log.info("Extracting text from the model response...")
        try:
            texts = []
            candidates = getattr(response, "candidates", [])
            for cand in candidates:
                parts = getattr(cand.content, "parts", [])
                for part in parts:
                    if hasattr(part, "text") and isinstance(part.text, str):
                        clean_text = part.text.strip()
                        if clean_text:
                            texts.append(clean_text)
            final_text = "\n".join(texts).strip()
            if not final_text:
                raise ValueError("No valid text extracted")
            return final_text
        except Exception as e:
            self.log.info(f"Text extraction fallback used: {e}")
            fallback = getattr(response, "text", "")
            return fallback.strip() if fallback else ""
