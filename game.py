import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class BikeSharingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("共享单车投放管理游戏")
        self.master.geometry("1000x600")  # 设置窗口初始大小

        # 基本参数设置
        self.city_population = 120000  # 城市人口数量
        self.current_bikes = 1000  # 当前共享单车数量
        self.maintenance_cost = 2500  # 每日单车维护成本
        self.rent_price = 2  # 每次租赁价格
        self.damage_rate = 0.05  # 每日单车损坏率

        # 政策相关参数
        self.policy_effect = 2.0  # 政策对租赁率的影响系数，初始为2（无影响）
        self.policy_range = (0, 4)  # 政策力度的范围（0到4）

        # 用户满意度相关参数
        self.user_satisfaction = 50  # 初始用户满意度（范围0-100）
        self.satisfaction_threshold = 40  # 用户满意度低于此值会影响租赁率

        # 天气相关参数
        self.weather_effect = {
            "sunny": 1.3,
            "cloudy": 1.0,
            "rainy": 0.6
        }
        self.current_weather = "cloudy"  # 初始天气

        # 时间段相关参数
        self.time_slot_effect = {
            "morning_rush": 1.5,
            "daytime": 1.0,
            "evening_rush": 1.5,
            "night": 0.5
        }
        self.current_time_slot = "daytime"  # 初始时间段

        # 收入和天数相关参数
        self.total_income = 0  # 总收入
        self.day = 1  # 当前天数
        self.round = 1  # 当前轮数

        # 竞争对手相关参数
        self.competitor_presence = False  # 是否有竞争对手进入市场
        self.competitor_effect = 0.7  # 竞争对手进入后对租赁率的影响系数

        self.daily_profits = []  # 记录每日利润
        self.daily_satisfactions = []  # 记录每日满意度

        self.create_widgets()

    def create_widgets(self):
        # 创建左右框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧操作区域（可滚动）
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建画布和滚动条
        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 显示游戏信息标签
        self.info_label = ttk.Label(scrollable_frame, text=f"城市人口: {self.city_population}\n"
                                                           f"当前共享单车数量: {self.current_bikes}\n"
                                                           f"每日维护成本: ${self.maintenance_cost}\n"
                                                           f"每次租赁价格: ${self.rent_price}\n"
                                                           f"当前政策力度系数: {self.policy_effect}\n"
                                                           f"用户满意度: {self.user_satisfaction}\n"
                                                           f"当前天气: {self.current_weather}\n"
                                                           f"当前时间段: {self.current_time_slot}\n"
                                                           f"总收入: ${self.total_income}\n"
                                                           f"当前天数: {self.day}，当前轮数: {self.round}\n"
                                                           f"是否有竞争对手: {'是' if self.competitor_presence else '否'}",
                                    justify=tk.LEFT)
        self.info_label.pack(pady=10, fill=tk.X)

        # 投放单车数量输入相关组件
        add_bikes_frame = ttk.LabelFrame(scrollable_frame, text="投放共享单车")
        add_bikes_frame.pack(fill=tk.X, pady=5)

        self.add_bikes_label = ttk.Label(add_bikes_frame, text="输入要投放的共享单车数量:")
        self.add_bikes_label.pack(anchor=tk.W, padx=5)

        self.add_bikes_entry = ttk.Entry(add_bikes_frame)
        self.add_bikes_entry.pack(fill=tk.X, padx=5, pady=5)

        self.add_bikes_button = ttk.Button(add_bikes_frame, text="投放共享单车", command=self.add_bikes)
        self.add_bikes_button.pack(pady=5)

        # 政策调整相关组件
        policy_frame = ttk.LabelFrame(scrollable_frame, text="政策调整")
        policy_frame.pack(fill=tk.X, pady=5)

        self.policy_label = ttk.Label(policy_frame,
                                      text=f"输入鼓励骑行政策力度（{self.policy_range[0]} - {self.policy_range[1]}之间的数值，2表示无影响）:")
        self.policy_label.pack(anchor=tk.W, padx=5)

        self.policy_entry = ttk.Entry(policy_frame)
        self.policy_entry.pack(fill=tk.X, padx=5, pady=5)
        self.policy_entry.insert(0, "2")

        self.policy_button = ttk.Button(policy_frame, text="实施政策", command=self.apply_policy)
        self.policy_button.pack(pady=5)

        # 天气设置相关组件
        weather_frame = ttk.LabelFrame(scrollable_frame, text="天气设置")
        weather_frame.pack(fill=tk.X, pady=5)

        self.weather_label = ttk.Label(weather_frame, text="设置当天天气（sunny/cloudy/rainy）:")
        self.weather_label.pack(anchor=tk.W, padx=5)

        self.weather_entry = ttk.Entry(weather_frame)
        self.weather_entry.pack(fill=tk.X, padx=5, pady=5)
        self.weather_entry.insert(0, "cloudy")

        self.weather_button = ttk.Button(weather_frame, text="设置天气", command=self.set_weather)
        self.weather_button.pack(pady=5)

        # 时间段设置相关组件
        time_slot_frame = ttk.LabelFrame(scrollable_frame, text="时间段设置")
        time_slot_frame.pack(fill=tk.X, pady=5)

        self.time_slot_label = ttk.Label(time_slot_frame,
                                         text="设置当天时间段（morning_rush/daytime/evening_rush/night）:")
        self.time_slot_label.pack(anchor=tk.W, padx=5)

        self.time_slot_entry = ttk.Entry(time_slot_frame)
        self.time_slot_entry.pack(fill=tk.X, padx=5, pady=5)
        self.time_slot_entry.insert(0, "daytime")

        self.time_slot_button = ttk.Button(time_slot_frame, text="设置时间段", command=self.set_time_slot)
        self.time_slot_button.pack(pady=5)

        # 竞争对手相关组件
        competitor_frame = ttk.LabelFrame(scrollable_frame, text="竞争对手")
        competitor_frame.pack(fill=tk.X, pady=5)

        self.competitor_button = ttk.Button(competitor_frame, text="让竞争对手进入市场", command=self.spawn_competitor)
        self.competitor_button.pack(pady=5)

        # 结束当天按钮
        end_day_frame = ttk.LabelFrame(scrollable_frame, text="结束当天")
        end_day_frame.pack(fill=tk.X, pady=10)

        self.end_day_button = ttk.Button(end_day_frame, text="结束当天", command=self.end_day)
        self.end_day_button.pack(pady=5)

        # 显示规则按钮
        rule_frame = ttk.LabelFrame(scrollable_frame, text="游戏规则")
        rule_frame.pack(fill=tk.X, pady=5)

        self.rule_button = ttk.Button(rule_frame, text="显示游戏规则", command=self.show_rules)
        self.rule_button.pack(pady=5)

        # 右侧图表区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建图表
        self.figure, (self.ax_profit, self.ax_satisfaction) = plt.subplots(2, 1, figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_chart(self):
        self.ax_profit.clear()
        self.ax_satisfaction.clear()

        if self.daily_profits:
            days = list(range(1, len(self.daily_profits) + 1))

            self.ax_profit.plot(days, self.daily_profits, marker='o')
            self.ax_profit.set_title("每日利润")
            self.ax_profit.set_xlabel("天数")
            self.ax_profit.set_ylabel("利润（元）")
            self.ax_profit.grid(True)

            self.ax_satisfaction.plot(days, self.daily_satisfactions, marker='o', color='green')
            self.ax_satisfaction.set_title("每日用户满意度")
            self.ax_satisfaction.set_xlabel("天数")
            self.ax_satisfaction.set_ylabel("满意度")
            self.ax_satisfaction.grid(True)

            self.figure.tight_layout()
            self.canvas.draw()

    def add_bikes(self):
        try:
            num_bikes = int(self.add_bikes_entry.get())
            if num_bikes < 0:
                raise ValueError
            self.current_bikes += num_bikes
            self.update_info()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的正整数")

    def apply_policy(self):
        try:
            new_policy_effect = float(self.policy_entry.get())
            if new_policy_effect < self.policy_range[0] or new_policy_effect > self.policy_range[1]:
                raise ValueError
            self.policy_effect = new_policy_effect
            self.update_info()
        except ValueError:
            messagebox.showerror("错误", f"请输入{self.policy_range[0]} - {self.policy_range[1]}之间的有效数值")

    def set_weather(self):
        weather = self.weather_entry.get().lower()
        if weather in self.weather_effect:
            self.current_weather = weather
            self.update_info()
        else:
            messagebox.showerror("错误", "请输入有效的天气类型（sunny/cloudy/rainy）")

    def set_time_slot(self):
        time_slot = self.time_slot_entry.get().lower()
        if time_slot in self.time_slot_effect:
            self.current_time_slot = time_slot
            self.update_info()
        else:
            messagebox.showerror("错误", "请输入有效的时间段（morning_rush/daytime/evening_rush/night）")

    def spawn_competitor(self):
        if not self.competitor_presence:
            self.competitor_presence = True
            messagebox.showinfo("通知", "竞争对手已进入市场，租赁率将受到影响！")
            self.update_info()
        else:
            messagebox.showinfo("通知", "已经有竞争对手存在，无需再次操作。")

    def calculate_daily_rentals(self):
        # 计算基础租赁率
        base_rental_rate = min(self.current_bikes / self.city_population * 0.6, 0.6) * self.policy_effect
        # 考虑天气、时间段、用户满意度和竞争对手的影响
        weather_factor = self.weather_effect[self.current_weather]
        time_slot_factor = self.time_slot_effect[self.current_time_slot]
        satisfaction_factor = 1 - max(0, (self.satisfaction_threshold - self.user_satisfaction)) / 100
        competitor_factor = self.competitor_effect if self.competitor_presence else 1
        rental_rate = base_rental_rate * weather_factor * time_slot_factor * satisfaction_factor * competitor_factor
        self.daily_rentals = int(self.city_population * rental_rate * (random.uniform(0.8, 1.2)))

    def end_day(self):
        self.calculate_daily_rentals()

        # 计算当天收入
        daily_income = self.daily_rentals * self.rent_price

        # 计算当天净利润
        daily_profit = daily_income - self.maintenance_cost

        self.total_income += daily_profit
        self.daily_profits.append(daily_profit)

        # 模拟共享单车损坏
        bikes_lost = int(self.current_bikes * self.damage_rate)
        self.current_bikes -= bikes_lost

        # 根据当天租赁情况和单车数量调整用户满意度
        if self.daily_rentals > 0.8 * self.current_bikes:
            self.user_satisfaction = min(100, self.user_satisfaction + 10)
        elif self.daily_rentals < 0.2 * self.current_bikes:
            self.user_satisfaction = max(0, self.user_satisfaction - 15)

        self.daily_satisfactions.append(self.user_satisfaction)
        self.update_info()
        self.update_chart()  # 更新图表
        self.show_daily_report()
        self.evaluate_day()

        self.day += 1
        if self.day > 3:
            self.day = 1
            self.show_round_chart()
            self.round += 1
            if self.round > 3:
                messagebox.showinfo("游戏结束", "游戏已全部结束，感谢游玩！")
                self.master.destroy()
            else:
                self.continue_round()

    def update_info(self):
        self.info_label.config(text=f"城市人口: {self.city_population}\n"
                                    f"当前共享单车数量: {self.current_bikes}\n"
                                    f"每日维护成本: ${self.maintenance_cost}\n"
                                    f"每次租赁价格: ${self.rent_price}\n"
                                    f"当前政策力度系数: {self.policy_effect}\n"
                                    f"用户满意度: {self.user_satisfaction}\n"
                                    f"当前天气: {self.current_weather}\n"
                                    f"当前时间段: {self.current_time_slot}\n"
                                    f"总收入: ${self.total_income}\n"
                                    f"当前天数: {self.day}，当前轮数: {self.round}\n"
                                    f"是否有竞争对手: {'是' if self.competitor_presence else '否'}")

    def show_daily_report(self):
        report = f"第 {self.round} 轮，第 {self.day} 天报告:\n"
        report += f"今日租赁次数: {self.daily_rentals}\n"
        report += f"今日收入: ${self.daily_rentals * self.rent_price}\n"
        report += f"今日净利润: ${self.daily_rentals * self.rent_price - self.maintenance_cost}\n"
        report += f"剩余共享单车数量: {self.current_bikes}\n"
        report += f"用户满意度: {self.user_satisfaction}\n"
        messagebox.showinfo("每日报告", report)

    def evaluate_day(self):
        # 综合考虑利润和用户满意度进行评级
        if self.total_income > 5000 and self.user_satisfaction > 80:
            rating = "优秀，当天运营表现极为出色！"
        elif self.total_income > 2000 and self.user_satisfaction > 60:
            rating = "良好，当天运营状况良好，利润和满意度都不错。"
        elif self.total_income > 0 and self.user_satisfaction > 40:
            rating = "合格，当天基本实现盈利，用户满意度尚可。"
        else:
            rating = "欠佳，当天运营存在较大问题，利润和满意度有待提高。"

        messagebox.showinfo("当天评级", f"第 {self.round} 轮，第 {self.day} 天的评级为：{rating}")

    def show_rules(self):
        rules = "游戏规则:\n"
        rules += "1. 你是共享单车公司的管理者，目标是通过合理管理实现盈利并维持较高的用户满意度。\n"
        rules += "2. 游戏共设置3轮，每轮3天，轮数为1-3。各轮之间有逻辑承接性，上一轮的结果会影响下一轮的初始状态。\n"
        rules += "3. 可以输入要投放的共享单车数量，点击“投放共享单车”增加单车数量。\n"
        rules += "4. 输入0到4之间的数值来设置鼓励骑行政策力度，2表示无影响，大于2促进租赁，小于2抑制租赁，点击“实施政策”应用政策。\n"
        rules += "5. 输入当天的天气情况（sunny/cloudy/rainy），点击“设置天气”来影响当天的租赁次数。晴天会增加租赁次数，雨天会减少租赁次数。\n"
        rules += "6. 输入当天的时间段（morning_rush/daytime/evening_rush/night），点击“设置时间段”来影响当天的租赁次数。早高峰和晚高峰租赁需求较高，夜间租赁需求较低。\n"
        rules += "7. 你可以选择是否让竞争对手进入市场，竞争对手进入会降低租赁率。\n"
        rules += "8. 每天结束时，系统会计算当天的租赁次数、收入、净利润和损坏的单车数量，并根据当天租赁情况调整用户满意度。\n"
        rules += "9. 每天结束会根据当天的净利润和用户满意度进行评级：\n"
        rules += "   - 若净利润 > 5000 且 用户满意度 > 80，获得优秀评级。\n"
        rules += "   - 若净利润 > 2000 且 用户满意度 > 60，获得良好评级。\n"
        rules += "   - 若净利润 > 0 且 用户满意度 > 40，获得合格评级。\n"
        rules += "   - 其他情况为欠佳评级。\n"
        rules += "10. 如果在游戏过程中共享单车数量降为0或总收入变为负数，游戏提前结束。\n"
        messagebox.showinfo("游戏规则", rules)

    def continue_round(self):
        # 这里可以设置每轮之间的逻辑承接，比如根据上一轮的表现调整一些参数
        # 例如，如果上一轮整体评级较高，可以适当减少维护成本，反之增加一些随机挑战
        last_round_rating = self.get_last_round_rating()
        if last_round_rating == "优秀":
            self.maintenance_cost = int(self.maintenance_cost * 0.9)
            messagebox.showinfo("新一轮开始", f"上一轮表现优秀，本轮每日维护成本降低为 ${self.maintenance_cost}")
        elif last_round_rating == "欠佳":
            # 增加一些随机挑战，比如增加损坏率
            self.damage_rate = min(0.1, self.damage_rate + 0.02)
            messagebox.showinfo("新一轮开始", f"上一轮表现欠佳，本轮单车损坏率增加为 {self.damage_rate * 100}%")

    def get_last_round_rating(self):
        # 简单模拟获取上一轮的平均评级，这里假设只记录最后一天的评级作为上一轮评级
        # 实际可以更复杂地计算上一轮3天的综合评级
        return self.last_day_rating if hasattr(self, 'last_day_rating') else "合格"

    def show_round_chart(self):
        days = np.arange(1, len(self.daily_profits) + 1)
        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.plot(days, self.daily_profits, marker='o')
        plt.title(f"第 {self.round - 1} 轮每日利润")
        plt.xlabel("天数")
        plt.ylabel("利润（元）")

        plt.subplot(1, 2, 2)
        plt.plot(days, self.daily_satisfactions, marker='o', color='green')
        plt.title(f"第 {self.round - 1} 轮每日用户满意度")
        plt.xlabel("天数")
        plt.ylabel("满意度")

        plt.tight_layout()
        plt.show()
        self.daily_profits = []
        self.daily_satisfactions = []


if __name__ == "__main__":
    root = tk.Tk()
    game = BikeSharingGame(root)
    root.mainloop()
