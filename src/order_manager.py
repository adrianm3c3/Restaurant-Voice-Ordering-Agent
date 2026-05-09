import copy


class OrderManager:
    def __init__(self):
        self.order = []

    def add_item(self, item):
        """
        Adds item to order.
        If identical item exists, increase quantity.
        """
        clean_item = copy.deepcopy(item)

        for existing in self.order:
            if self._items_equal(existing, clean_item):
                existing["quantity"] = (
                    existing.get("quantity", 1)
                    + clean_item.get("quantity", 1)
                )
                return

        self.order.append(clean_item)

    def remove_last_item(self, quantity=1):
        if not self.order:
            return None
        return self._decrement_or_remove(len(self.order) - 1, quantity)

    def remove_item_by_name(self, name, quantity=None, size=None):
        for i in range(len(self.order) - 1, -1, -1):
            item = self.order[i]

            if item.get("type") == "pizza" and item.get("base") == name:
                if size is None or item.get("size") == size:
                    return self._decrement_or_remove(i, quantity)

            if item.get("name") == name:
                return self._decrement_or_remove(i, quantity)

        return None

    def remove_last_pizza(self, quantity=None, size=None):
        for i in range(len(self.order) - 1, -1, -1):
            item = self.order[i]

            if item.get("type") == "pizza":
                if size is None or item.get("size") == size:
                    return self._decrement_or_remove(i, quantity)

        return None

    def modify_last_pizza(self, action, toppings):
        """
        Modify the most recent pizza in the order.
        Supported actions:
        - remove_topping
        - remove_toppings
        - add_topping
        - add_toppings
        """
        if isinstance(toppings, str):
            toppings = [toppings]

        for i in range(len(self.order) - 1, -1, -1):
            item = self.order[i]

            if item.get("type") != "pizza":
                continue

            item_toppings = item.setdefault("toppings", [])
            removals = item.setdefault("removals", [])

            for topping in toppings:
                if action in {"remove_topping", "remove_toppings"}:
                    if topping in item_toppings:
                        item_toppings.remove(topping)
                    elif topping not in removals:
                        removals.append(topping)

                elif action in {"add_topping", "add_toppings"}:
                    if topping in removals:
                        removals.remove(topping)

                    if topping not in item_toppings:
                        item_toppings.append(topping)

                else:
                    return None

            return copy.deepcopy(item)

        return None

    def _decrement_or_remove(self, index, quantity):
        item = self.order[index]
        current_qty = item.get("quantity", 1)

        removed_item = copy.deepcopy(item)

        if quantity is None:
            return copy.deepcopy(self.order.pop(index))

        if quantity >= current_qty:
            return copy.deepcopy(self.order.pop(index))

        item["quantity"] = current_qty - quantity
        removed_item["quantity"] = quantity

        return removed_item

    def get_order(self):
        return copy.deepcopy(self.order)

    def clear_order(self):
        self.order = []

    def is_empty(self):
        return len(self.order) == 0

    def _items_equal(self, item1, item2):
        """
        Determines if two items are identical for merging.
        """
        if item1.get("type") != item2.get("type"):
            return False

        if item1["type"] == "pizza":
            return (
                item1.get("base") == item2.get("base")
                and item1.get("size") == item2.get("size")
                and item1.get("crust") == item2.get("crust")
                and sorted(item1.get("toppings", [])) == sorted(item2.get("toppings", []))
                and sorted(item1.get("removals", [])) == sorted(item2.get("removals", []))
            )
    
    

        return item1.get("name") == item2.get("name")
    
    def change_last_pizza_crust(self, crust):
        for i in range(len(self.order) - 1, -1, -1):
            item = self.order[i]

            if item.get("type") == "pizza":
                item["crust"] = crust
                return copy.deepcopy(item)

        return None
