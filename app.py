"""
Candlestick OHLC Converter
---------------------------
Desktop GUI (Tkinter) to convert a plain list of numbers into OHLC
candles and render them as a real candlestick chart (mplfinance),
with optional technical indicators.

Run:
    python app.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import mplfinance as mpf

from core import numbers_to_ohlc, load_numbers_from_file, parse_numbers_text
import indicators as ind


class CandlestickApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تبدیل اعداد به نمودار کندل‌استیک (OHLC)")
        self.geometry("1150x780")

        self.ohlc_df = None
        self.canvas = None
        self.toolbar = None

        self._build_ui()

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        # --- Input numbers box ---
        input_frame = ttk.LabelFrame(top, text="۱) وارد کردن اعداد", padding=8)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.numbers_text = tk.Text(input_frame, height=8, width=40)
        self.numbers_text.pack(fill=tk.BOTH, expand=True)
        self.numbers_text.insert(
            "1.0",
            "اعداد را با فاصله، کاما یا هر خط جدید وارد کنید\n"
            "مثال: 10 12 9 15 14 16 13 18",
        )
        self.numbers_text.bind("<FocusIn>", self._clear_placeholder)

        load_btn = ttk.Button(input_frame, text="بارگذاری از فایل CSV/Excel", command=self._load_file)
        load_btn.pack(fill=tk.X, pady=(6, 0))

        # --- Settings box ---
        settings_frame = ttk.LabelFrame(top, text="۲) تنظیمات کندل", padding=8)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Label(settings_frame, text="تعداد عدد در هر کندل:").pack(anchor="w")
        self.group_size_var = tk.IntVar(value=4)
        group_spin = ttk.Spinbox(settings_frame, from_=2, to=1000, textvariable=self.group_size_var, width=10)
        group_spin.pack(anchor="w", pady=(0, 10))

        ttk.Label(settings_frame, text="اندیکاتورها:").pack(anchor="w")
        self.ma_var = tk.BooleanVar(value=False)
        self.bb_var = tk.BooleanVar(value=False)
        self.rsi_var = tk.BooleanVar(value=False)
        self.macd_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Moving Average", variable=self.ma_var).pack(anchor="w")
        ttk.Checkbutton(settings_frame, text="Bollinger Bands", variable=self.bb_var).pack(anchor="w")
        ttk.Checkbutton(settings_frame, text="RSI", variable=self.rsi_var).pack(anchor="w")
        ttk.Checkbutton(settings_frame, text="MACD", variable=self.macd_var).pack(anchor="w")

        gen_btn = ttk.Button(settings_frame, text="تولید نمودار", command=self._generate_chart)
        gen_btn.pack(fill=tk.X, pady=(14, 4))

        export_btn = ttk.Button(settings_frame, text="خروجی OHLC (CSV)", command=self._export_csv)
        export_btn.pack(fill=tk.X)

        # --- Chart area ---
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _clear_placeholder(self, event):
        if self.numbers_text.get("1.0", "end").strip().startswith("اعداد را"):
            self.numbers_text.delete("1.0", "end")
        self.numbers_text.unbind("<FocusIn>")

    # ------------------------------------------------------------ actions
    def _load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.csv *.xlsx *.xls"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            numbers = load_numbers_from_file(path)
        except Exception as e:
            messagebox.showerror("خطا در خواندن فایل", str(e))
            return

        self.numbers_text.delete("1.0", "end")
        self.numbers_text.insert("1.0", " ".join(str(n) for n in numbers))
        messagebox.showinfo("موفق", f"{len(numbers)} عدد از فایل بارگذاری شد")

    def _get_numbers(self):
        text = self.numbers_text.get("1.0", "end")
        return parse_numbers_text(text)

    def _build_ohlc(self):
        numbers = self._get_numbers()
        group_size = self.group_size_var.get()
        df = numbers_to_ohlc(numbers, group_size)
        self.ohlc_df = df
        return df

    def _generate_chart(self):
        try:
            df = self._build_ohlc()
        except Exception as e:
            messagebox.showerror("خطا", str(e))
            return

        addplots = []

        if self.ma_var.get():
            ma = ind.moving_average(df, window=min(20, max(2, len(df) // 2)))
            addplots.append(mpf.make_addplot(ma, color="orange", width=1.2))

        if self.bb_var.get():
            bb = ind.bollinger_bands(df, window=min(20, max(2, len(df) // 2)))
            addplots.append(mpf.make_addplot(bb["BB_Upper"], color="royalblue", width=0.9))
            addplots.append(mpf.make_addplot(bb["BB_Mid"], color="gray", width=0.8, linestyle="--"))
            addplots.append(mpf.make_addplot(bb["BB_Lower"], color="royalblue", width=0.9))

        panel_count = 1
        if self.rsi_var.get():
            rsi_vals = ind.rsi(df, window=min(14, max(2, len(df) // 2)))
            addplots.append(mpf.make_addplot(rsi_vals, panel=panel_count, color="purple", ylabel="RSI"))
            panel_count += 1

        if self.macd_var.get():
            macd_df = ind.macd(df)
            addplots.append(mpf.make_addplot(macd_df["MACD"], panel=panel_count, color="blue", ylabel="MACD"))
            addplots.append(mpf.make_addplot(macd_df["Signal"], panel=panel_count, color="red"))
            addplots.append(mpf.make_addplot(macd_df["Histogram"], panel=panel_count, type="bar", color="dimgray", alpha=0.5))
            panel_count += 1

        # clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        style = mpf.make_mpf_style(base_mpf_style="charles", rc={"font.size": 8})

        kwargs = dict(
            type="candle",
            style=style,
            volume=False,
            addplot=addplots if addplots else None,
            returnfig=True,
        )
        try:
            fig, axes = mpf.plot(df, **kwargs)
        except Exception as e:
            messagebox.showerror("خطا در رسم نمودار", str(e))
            return

        fig.set_size_inches(10.5, 6.5)

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame)
        self.toolbar.update()

    def _export_csv(self):
        if self.ohlc_df is None:
            messagebox.showwarning("توجه", "ابتدا نمودار را تولید کنید")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        self.ohlc_df.to_csv(path, encoding="utf-8-sig")
        messagebox.showinfo("موفق", f"فایل ذخیره شد:\n{path}")


if __name__ == "__main__":
    app = CandlestickApp()
    app.mainloop()
