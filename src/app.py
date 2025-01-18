from topic_handler import create_topic_chain

topic = 'cats'

chain = create_topic_chain()
result = chain.invoke({'user_input': input_text})