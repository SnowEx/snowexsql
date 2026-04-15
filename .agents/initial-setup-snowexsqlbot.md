I would like to build a prototype of https://github.com/uw-ssec/llmaven. 

I will be using these RSE plugins with Claude Code command line: https://github.com/uw-ssec/rse-plugins and following the "research", "plan", "implement" protocol.

My prototype example is going to be the NASA SnowEx mission. I am a core developer for the API and SQL database currently posted here: https://github.com/SnowEx/snowexsql. My goal is to showcase a "snowexsql-bot" that can answer questions about the mission, and that also enables plain language querying of the database.

Here is my general plan:

* gather all relevant scientific and technical literature on snowex and the associated open source software and datasets surrounding it
* build an MCP server to establish protocols for database querying (this is something I already initiated in a local branch)
* build agents and skills to set guardrails on the capabilities and components of the LLM
* build a custom RAG LLM to be deployed locally, using open source weightings on hugging face
* implement the custom LLM via the SSEC recommended agentic RAG approach
* test, iterate and improve
* deploy to AWS

My resources include free AWS credits, a Windows 11 laptop with 16 GB RAM and using WSL2 in VSCode.

Help me get set up for my first prompt to Claude within the RSE "research" plugin and let me know if I've missed anything important.

