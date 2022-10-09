class WaifuAI():
  @staticmethod
  def setattrs(base_situation: str, user_id: str):
    WaifuAI.base_situation = base_situation
    WaifuAI.user_id = user_id
    WaifuAI.situation = [base_situation]
  
  @staticmethod
  def append_situation(situation: str):
    WaifuAI.situation.append(situation)

  @staticmethod
  def reset_situation():
    WaifuAI.situation = [WaifuAI.base_situation]

class Seller(WaifuAI):
  def __init__(self, name: str, stock: dict):
    self.name = name
    self.stock = stock
    self.sync_stock()

  def sync_stock(self):
    for merch, v in self.stock.items():
      qnty = v[0]
      price = v[1]
      if qnty != 0:
        super().append_situation(f"{self.name} може продати {merch} у кількості {qnty} за ціною {price} гривень.")
      else:
        super().append_situation(f"{merch} закінчився, тому {self.name} не може продати {merch}.")
  
  def get_order(self, message, tolerance=70):
    import re
    from fuzzywuzzy import fuzz

    match_obj = re.match("купити ([\w\s]*)\.", message)
    if match_obj:
      finded_merch = match_obj.groups()[0]

      max_ratio = 0
      merch = None
      for stock_merch in self.stock.keys():
        ratio = fuzz.ratio(finded_merch, stock_merch)

        if ratio > max_ratio or max_ratio == 0:
          max_ratio = ratio
          merch = stock_merch

      if max_ratio >= tolerance and merch is not None:
        return merch
      return "Not Found"
    return None

class Customer(WaifuAI):
  def __init__(self, name: str, cash: float):
    self.name = name
    self.cash = cash
    self.sync_cash()

  def sync_cash(self):
    super().append_situation(f"{self.name} має при собі {self.cash} гривень.")

  def purchase(self, seller: Seller, merch):
    if merch == "Not Found":
      super().situation.append(f"{self.name} намагався купити товар, але {seller.name} не зрозуміла що це за товар.")
      return

    merch_qnty = seller.stock[merch][0]
    merch_price = seller.stock[merch][1]
    
    if merch_qnty == 0:
      super().append_situation(f"{self.name} намагався купити {merch}, але {merch} закінчився.")
      return

    if self.cash < merch_price:
      super().append_situation(f"{self.name} намагався купити {merch}, але {self.name} не має стільки грошей.")
      return

    seller.stock[merch][0] -= 1
    self.cash -= merch_price
    super().reset_situation()
    self.sync_cash()
    seller.sync_stock()


from merch_list import merch_list

#@title Ствоерення діючих осіб{ run: "auto", form-width: "50%" }
#@markdown Покупець
customer_name = "Тарас-кун" #@param {type: "raw"}
cash = 200 #@param {type:"number"}

#@markdown Продавець
seller_name =   "Акено-тян" #@param {type: "raw"}
situation = "Акено-тян продає аніме-товари в магазині." #@param {type: "raw"}

user_id = "ZOQVdLSxSduuFZsp3ptjPX0DyjM9rsD08CJFE5bqHydWF9bbWI6a8fqyWnFubvAe"

WaifuAI.setattrs(situation, user_id)

customer = Customer(customer_name, cash)
seller = Seller(seller_name, merch_list)

while(True):
  message = input()

  merch = seller.get_order(message)
  if merch is not None:
    customer.purchase(seller, merch)

  request_dict = {
    "from_name": customer.name,
    "to_name":   seller.name,
    "situation": WaifuAI.situation,
    "user_id":   WaifuAI.user_id,
    "message":   message
  }

  from pprint import pprint

  pprint(request_dict)

  if message == "q":
    break