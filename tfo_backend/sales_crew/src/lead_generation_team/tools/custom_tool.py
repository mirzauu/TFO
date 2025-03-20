from crewai_tools import tool

@tool
class LeadQualificationTool:
    """
    A custom tool to evaluate leads based on predefined criteria.
    It processes input lead data and returns categorized leads.
    """

    def __init__(self, criteria=None):
        """
        Initializes the tool with optional custom criteria.
        Args:
            criteria (dict): A dictionary of qualification criteria.
                             Example: {"industry": "Tech", "size": "50-500 employees"}
        """
        self.criteria = criteria or {}

    def __call__(self, lead_data: list) -> str:
        """
        Processes the lead data to qualify leads.
        Args:
            lead_data (list): A list of dictionaries representing leads.
                              Each lead should have the required keys for evaluation.
        Returns:
            str: Categorized leads as a string in a human-readable format.
        """
        qualified_leads = []
        unqualified_leads = []

        for lead in lead_data:
            if self._is_qualified(lead):
                qualified_leads.append(lead)
            else:
                unqualified_leads.append(lead)

        return self._format_output(qualified_leads, unqualified_leads)

    def _is_qualified(self, lead: dict) -> bool:
        """
        Evaluates if a lead meets the qualification criteria.
        Args:
            lead (dict): A dictionary containing lead details.
        Returns:
            bool: True if the lead qualifies, False otherwise.
        """
        for key, value in self.criteria.items():
            if key not in lead or lead[key] != value:
                return False
        return True

    def _format_output(self, qualified: list, unqualified: list) -> str:
        """
        Formats the output as a human-readable string.
        Args:
            qualified (list): List of qualified leads.
            unqualified (list): List of unqualified leads.
        Returns:
            str: Formatted output.
        """
        output = "Qualified Leads:\n"
        for lead in qualified:
            output += f"- {lead}\n"

        output += "\nUnqualified Leads:\n"
        for lead in unqualified:
            output += f"- {lead}\n"

        return output
