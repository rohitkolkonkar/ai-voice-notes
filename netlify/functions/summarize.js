exports.handler = async function (event, context) {
  // Only allow POST requests
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  // Use environment variable if available in Netlify, otherwise use the provided key
  const GROQ_API_KEY = process.env.GROQ_API_KEY;

  try {
    const { transcript } = JSON.parse(event.body);

    if (!transcript) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Transcript is required" })
      };
    }

    const payload = {
      model: "llama-3.1-8b-instant",
      messages: [
        {
          role: "system",
          content: "You are an expert at extracting structured intelligence from voice notes and meeting transcripts.\nReturn ONLY a JSON object with NO markdown, NO backticks, NO preamble. Exactly this shape:\n{\n  \"tldr\": \"One crisp sentence capturing the core message.\",\n  \"keyPoints\": [\"point 1\", \"point 2\", \"point 3\"],\n  \"actionItems\": [\"action 1\", \"action 2\", \"action 3\"],\n  \"sentiment\": \"positive|neutral|urgent|mixed\",\n  \"wordCount\": 120\n}\nRules: keyPoints = 3-5 insight bullets. actionItems = 2-6 concrete tasks (start each with a verb). Keep everything under 20 words per item."
        },
        {
          role: "user",
          content: `Voice note transcript:\n\n"${transcript}"`
        }
      ],
      response_format: { type: "json_object" }
    };

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        statusCode: response.status,
        body: JSON.stringify({ error: data.error?.message || "API Error" })
      };
    }

    const raw_content = data.choices[0].message.content || "{}";

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ result: raw_content })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
