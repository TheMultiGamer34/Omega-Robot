"""Main file, intended to be launched."""

__version__ = "under developpement"

import json
import discord
from discord import Intents
from discord.ext import commands
from cogs.omega import Omega
from cogs.moderation import Moderation
from cogs.fun import Fun, Confession
from logs.logger import logger


########################
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
import ast


def get_response(message):
    with open("./save_file.txt", "r", encoding="utf-8") as f:
        y_train_dict_start = f.read()

        y_train_dict_start = ast.literal_eval(y_train_dict_start)

    corpus_entrainement = y_train_dict_start
    corpus_test = {"file_test": [message]}

    bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b')


    X_train = []
    y_train = []

    for file, messages_rules in corpus_entrainement.items():
        for message, rule in messages_rules.items():
            X_train.append(message)
            y_train.append(rule)


    X_train_transformed = bigram_vectorizer.fit_transform(X_train).toarray()
    X_test = {filename: bigram_vectorizer.transform(texts).toarray() for filename, texts in corpus_test.items()}


    clf = DecisionTreeClassifier()  #Validé
    #clf = GaussianNB()              #Validé
    #clf = SVC()                     #Non validé
    #clf = MultinomialNB()           #Non validé


    clf.fit(X_train_transformed, y_train)


    predictions = {}
    for filename, X in X_test.items():
        predicted = clf.predict(X)
        predictions[filename] = predicted.tolist()


    return [{filename: prediction} for filename, prediction in predictions.items()]


#################################










with open("config.json", encoding="utf-8") as file:
    config = json.load(file)

class Bot(commands.Bot):
    """Encapsulate a discord bot."""
    extensions = (
        Fun,
        Moderation,
        Omega
    )

    optionals = {
        Confession: config["CONFESSION"]["ENABLED"]
    }

    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(config["PREFIX"], intents=intents)

        self.description = "A bot for two Omega Discord servers."
        self.token = config["TOKEN"]

    async def on_ready(self):
        """Log information about bot launching."""
        logger.info("Bot %s connected on %s servers", self.user.name, len(self.guilds))

    async def on_message(self, message):
        """Handle incoming messages."""
        if message.author != self.user:
            logger.info("Received message: %s", message.content)
            if message.content.startswith('!hello'):
                await message.channel.send(f'Hello {message.author.name}!')

            response = list(main.get_response(message.content)[0].values())[0][0]
            logger.info("Response: %s", response)
            
            if response == "G12":
                await message.channel.send(f"<@&{discord.utils.get(message.guild.roles, name='Modérateurs').id}>")
        
        await self.process_commands(message)

    def run(self):
        """Start the bot and load one by one available cogs."""
        for cog in self.extensions:
            self.add_cog(cog(self, config))

        for cog, requirement in self.optionals.items():
            if requirement:
                self.add_cog(cog(self, config))

        super().run(self.token)

if __name__ == "__main__":
    omega_robot = Bot()
    omega_robot.run()
