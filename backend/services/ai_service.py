import os
import openai
import re
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_description(entity_type: str, entity_name: str, context: str) -> str:
    """
    Generate an AI description for a dbt model or column using OpenAI's API
    
    Args:
        entity_type: Either 'model' or 'column'
        entity_name: Name of the model or column
        context: SQL code or other context about the entity
    
    Returns:
        AI-generated description string
    """
    if not openai.api_key:
        return "AI description unavailable (API key not configured)"
    
    try:
        if entity_type == 'model':
            prompt = f"""
            You are a helpful data expert tasked with explaining dbt models.
            Based on the SQL code and model name below, write a clear, concise description (max 100 words)
            of what this model represents and what data it contains or transforms.
            
            Model name: {entity_name}
            
            SQL:
            {context}
            
            Description:
            """
        else:  # column
            prompt = f"""
            You are a helpful data expert tasked with explaining database columns.
            Based on the column name and SQL context below, write a clear, concise description (max 25 words)
            of what this column represents. Focus on the business meaning.
            
            Column name: {entity_name}
            
            Context:
            {context}
            
            Description:
            """
            
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates concise dbt documentation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        description = response.choices[0].message.content.strip()
        
        # Clean up the description
        description = re.sub(r'^["\']|["\']$', '', description)  # Remove quotes
        description = re.sub(r'\n+', ' ', description)  # Remove newlines
        
        return description
    
    except Exception as e:
        print(f"Error generating AI description: {e}")
        return f"AI description generation failed: {str(e)[:50]}..."

def get_model_suggestions(sql_code: str, existing_description: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate suggestions for improving a model, including tags and potential issues
    
    Args:
        sql_code: The SQL code of the model
        existing_description: Existing model description, if any
    
    Returns:
        Dictionary with suggestions
    """
    if not openai.api_key:
        return {"error": "API key not configured"}
    
    try:
        prompt = f"""
        Analyze this dbt model SQL code and provide the following:
        1. Three potential tags for categorizing this model
        2. Two potential data quality checks that would be appropriate
        3. One improvement suggestion for the SQL
        
        SQL Code:
        {sql_code}
        
        Existing description:
        {existing_description or "None"}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes SQL code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        
        # Extract tags
        tags_match = re.search(r'tags:?\s*(.+?)(?:\n\d|\Z)', content, re.DOTALL | re.IGNORECASE)
        tags = []
        if tags_match:
            tags_text = tags_match.group(1)
            tags = [t.strip() for t in re.findall(r'["\']?([^,"\']+)["\']?', tags_text) if t.strip()]
        
        # Extract quality checks
        checks_match = re.search(r'quality checks:?\s*(.+?)(?:\n\d|\Z)', content, re.DOTALL | re.IGNORECASE)
        checks = []
        if checks_match:
            checks_text = checks_match.group(1)
            checks = [c.strip() for c in re.split(r'\n\s*[-•*]\s*', checks_text) if c.strip()]
            checks = [c for c in checks if c and len(c) > 5]
        
        # Extract improvement
        improvement_match = re.search(r'improvement:?\s*(.+?)(?:\n\d|\Z)', content, re.DOTALL | re.IGNORECASE)
        improvement = ""
        if improvement_match:
            improvement = improvement_match.group(1).strip()
        
        return {
            "tags": tags,
            "quality_checks": checks,
            "improvement": improvement
        }
    
    except Exception as e:
        print(f"Error generating model suggestions: {e}")
        return {"error": str(e)} 