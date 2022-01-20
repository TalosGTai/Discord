import session
from discord.ext import commands
from discord.utils import get
from random import randint


class Games(commands.Cog):
    '''Игры'''
    def __init__(self, client) -> None:
        self.client = client


    @commands.cooldown(rate=1, per=1, type=commands.BucketType.user)
    @commands.command()
    async def duel(self, ctx, hero):
        '''Вызов на дуэль другого игрока
        
        Старайся вызывать более сильных противников, Геральт бы одобрил!

        Пример: .duel GTai 
        '''
        author = ctx.message.author.name
        user1 = session.find_user(author, session.all_users)
        user2 = session.find_user(hero, session.all_users)

        # Проверка дуэли с ботом или самим собой
        if user2 and user2.name == 'Dina':
            await ctx.send(f'Рано тебе ещё с ведьмачкой тягаться, смерд')
            print(f'Покушение на Дину')
        elif user2 and user1.name == user2.name:
            await ctx.send(f'С собой сражаться бессмысленно')
        else:
            # w1 - % победы 1ого игрока
            # w2 - % победы 2ого игрока
            # l1 = [1; w1]
            # l2 = [w1; 100]

            all_rate = user1.rate + user2.rate
            w1 = int(user1.rate / all_rate * 100)
            
            # чтобы не было дуэлей 100-0
            if w1 == 0:
                w1 = 1
            elif w1 == 100:
                w1 = 99

            w2 = 100 - w1 
            w = randint(1, 100)

            # для рандом на промежтке
            m1 = w1
            l1 = [i for i in range(1, m1 + 1)]

            money_win = min(w1, w2) * min(user2.money / 100, user1.money / 100)
            money_win = int(money_win * 100) / 100

            print('------------------------------------------------------')
            print(f'Была произведена дуэль между {user1.name} и {user2.name}')
            print(f'Рейтинги оппонентов {user1.rate} и {user2.rate}')
            print(f'Вероятность побед {w1}% и {w2}%')
            await ctx.send(f'Дуэль между {user1.name} {w1}% и {user2.name} {w2}%')

            if w in l1 or int(w1) == 100:
                user1.duel = self.update_stat(user1.duel, True)
                user2.duel = self.update_stat(user2.duel, False)

                if w1 < w2:
                    money_win *= (w2/w1)

                money_win = self.update_money(user1.money, money_win)

                print(f'{user1.name} одержал победу в дуэли над {user2.name}')
                await ctx.send(f'{user1.name} одержал победу в дуэли над {user2.name}')
                await ctx.send(f'И выиграл {money_win} монет')
                user1.money += money_win
                user2.money -= money_win
            else:
                user1.duel = self.update_stat(user1.duel, False)
                user2.duel = self.update_stat(user2.duel, True)

                if w2 < w1:
                    money_win *= (w1/w2)

                money_win = self.update_money(user1.money, money_win)

                print(f'{user2.name} одержал победу в дуэли над {user1.name}')
                await ctx.send(f'{user2.name} одержал победу в дуэли над {user1.name}')
                await ctx.send(f'И выиграл {money_win} монет')
                user1.money -= money_win
                user2.money += money_win

            print('------------------------------------------------------')


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def duel_top(self, ctx):
        '''Топ 5 дуэлянтов этой эпохи
        
        Сюда попадают лучшие из лучших
        Участвуй в дуэлях, выигрывай и станешь одним из них!
        
        Попасть можно только от 30 дуэлей
        '''
        author = ctx.message.author.name
        duel_stat = []
        for user in session.all_users:
            temp_stats = list(user.duel.split('-'))
            all_games = int(temp_stats[0])
            win_games = int(temp_stats[1])
            if win_games != 0:
                percent_win = int((win_games/all_games) * 100)
            else:
                percent_win = 0

            duel_stat.append((user.name, user.duel, percent_win))

        duel_stat = sorted(duel_stat, key=lambda user: user[2])
        
        j = len(duel_stat) - 1
        res = [duel_stat[i] for i in range(j, j - 5, -1)]
        
        print(f'{author} запросил топ 5 рейтинг дуэли')
        await ctx.send(f'Топ 5 лучших дуэлянтов этой эпохи:')
        for i in range(len(res)):
            await ctx.send(f'{i + 1} - {res[i][0]} {res[i][1]}')
       

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def duel_info(self, ctx, hero):
        '''Статистика в дуэлях
        
        Шаблон: .duel_info name
        Пример: .duel_info GTai
        '''
        author = ctx.message.author.name

        user = session.find_user(author, session.all_users)
        print(f'{author} запросил статы {user.name}')
        print(f'{user.duel_stats()}')
        await ctx.send(f'Статы {user.name}\n{user.duel_stats()}')


    def update_stat(self, stat, game):
        s = list(stat.split('-'))
        all_games = int(s[0]) + 1

        if game:
            win_games = int(s[1]) + 1
        else:
            win_games = int(s[1])

        res = str(all_games) + '-' + str(win_games)
        
        return res


    def update_money(self, user_money, money_win):
        # проверка на отрицательное количество монет
        if user_money - money_win < 0:
            money_win = user_money
        elif user_money == 0:
            money_win = 0
        
        # если по процентом вышел 0, но деньги есть у пользователя
        if money_win == 0 and user_money != 0:
            money_win = min(user_money, 1)

        money_win = int(money_win * 100) / 100

        return money_win


def setup(client):
    client.add_cog(Games(client))