# Inventory API — Session Review Notes

**Increment 1:** Python business logic  
**Session:** November 3, 2026  
**Purpose:** Close the gap between *recognizing* Python code and *constructing* it independently.

## 1. What we actually completed

- Chose a **dictionary of dictionaries**, keyed by integer product ID, as our in-memory inventory structure.
- Implemented `get_product(products, product_id)` using `.get()`; you reported **two passing pytest tests** (existing and missing IDs).
- Independently wrote the duplicate-ID check for `create_product()`.
- Independently constructed the inner product dictionary.
- Worked through the insertion statement and clarified assignment versus mutation.
- Identified your primary difficulty: **choosing and writing the correct data-structure operation without being shown options**.

> **Current status:** `create_product()` has its basic insertion logic, but **input validation and tests are not finished**. Do not treat it as a completed feature.

## 2. The inventory data model

```python
products = {
    101: {"name": "Keyboard", "price": 49.99, "quantity": 20},
    102: {"name": "Mouse", "price": 24.99, "quantity": 15},
}
```

- `products`: **outer dictionary**, the entire inventory.
- `product_id`: **key** in the outer dictionary (such as `101`).
- `product`: **inner dictionary**, one product record.
- `"name"`, `"price"`, `"quantity"`: keys in the inner dictionary.

The singular and plural variable names matter. Confusing `product` and `products` caused the main coding mistake today.

## 3. Operations to know — and when to use them

| Intention | Python | Behavior |
|---|---|---|
| Does ID 101 exist? | `101 in products` | `True` or `False`; checks dictionary **keys**. |
| Does ID 103 not exist? | `103 not in products` | `True` or `False`. |
| Retrieve a known ID | `products[101]` | Returns the record; raises `KeyError` if absent. |
| Retrieve a possibly missing ID | `products.get(103)` | Returns `None` if absent, unless a different default is supplied. |
| Read a product's quantity | `products[101]["quantity"]` | Selects the product, then its quantity. |
| Add or replace a product | `products[103] = product` | Adds if key is absent; replaces its value if present. |
| Update one field | `products[101]["quantity"] = 30` | Changes a field in an existing record. |
| Compare a value | `products[101]["quantity"] == 20` | Returns a Boolean; changes nothing. |
| Iterate product IDs | `for product_id in products:` | Iterates the outer dictionary's keys. |

**Selection rule:** First say what you want to do in English: *check existence*, *retrieve*, *insert/update*, *compare*, or *iterate*. Then choose the Python operation.

## 4. Assignment versus comparison

```python
quantity = 30      # Assignment: store a value
quantity == 30     # Comparison: evaluate True or False
```

The same distinction applies inside dictionaries:

```python
products[101]["quantity"] = 30   # Change the stored quantity
products[101]["quantity"] == 30  # Check whether quantity equals 30
```

Read `dictionary[key] = value` as **“put this value at this key in this dictionary.”**

## 5. The exact confusion we uncovered

These were the attempted insertion statements:

```python
product[product_id] += products  # Incorrect
products[product_id] = products # Incorrect
product[product_id] = products  # Incorrect
products[product_id] = product  # Correct
```

Why the last one works:

```text
DESTINATION[KEY] = ITEM
products[product_id] = product
```

- **Destination:** `products` — the entire inventory we want to modify.
- **Key:** `product_id` — where the record should be stored.
- **Item:** `product` — the single record we just constructed.

The first attempt also used `+=`, which is not the operation for inserting a dictionary entry.

**Before writing a dictionary assignment, ask:** Where does the value go? Under which key? What object am I storing?

## 6. Adding versus replacing

```python
products = {101: "Keyboard"}

products[102] = "Mouse"     # New key: ADD an entry
products[101] = "Monitor"   # Existing key: REPLACE its value
```

Both are **assignments**. Whether the result is insertion or replacement depends on whether the key already exists.

This is why `create_product()` checks for duplicates first: without that guard, assigning an existing product ID would overwrite its record.

## 7. Mutation versus rebinding

```python
products[102] = product  # MUTATION: change the existing dictionary's contents
products = product       # REBINDING: make the local name refer to another object
```

When a function receives a dictionary and modifies one of its entries, the caller sees the change because both references point to the same dictionary object.

Assigning a new object to the local parameter name `products` does **not** replace the caller's dictionary.

This matters for testing: checking only a function's return value does not prove that the original inventory was updated.

## 8. Navigating nested dictionaries

```python
record = products[101]            # First lookup: inner product dictionary
quantity = record["quantity"]    # Second lookup: quantity value

# Equivalent one-line expression:
quantity = products[101]["quantity"]
```

Read from left to right. After each lookup, ask: **What kind of object do I have now?**

- `products` → outer dictionary.
- `products[101]` → inner product dictionary.
- `products[101]["quantity"]` → quantity number.

## 9. Code written or discussed today

### `get_product()` — completed and tested

```python
def get_product(products: dict, product_id: int):
    return products.get(product_id)
```

`.get()` is appropriate here because a missing product is represented by `None`. You reported that the existing-ID and missing-ID tests passed.

### `create_product()` — assembled core logic, **not finished**

```python
def create_product(
    products: dict,
    product_id: int,
    name: str,
    price: float,
    quantity: int,
):
    if product_id in products:
        raise ValueError("This ID is in use. Try again")

    product = {
        "name": name,
        "price": price,
        "quantity": quantity,
    }

    products[product_id] = product
    return product
```

This is the **assembled version of the logic discussed**, not a claim that the complete function was independently tested.

**Remaining rules:** Reject blank names, negative prices, negative quantities, and non-integer quantities. Then write tests for successful creation and rejected inputs.

## 10. How to choose an operation without a quiz

1. **State the requirement in plain English.** Example: “Check if the ID already exists.”
2. **Identify the structure.** Here it's a dictionary, not a list.
3. **Identify the target.** Whole inventory, one product ID, or one field within a product?
4. **Choose the operation.** Membership (`in`), lookup (`[]` or `.get()`), assignment (`=`), comparison (`==`), iteration (`for`).
5. **Write the smallest statement.** Run it and inspect what changed or what was returned.

The goal is **recall and construction**, not picking an answer from a multiple-choice menu. It's fine to consult documentation if an operation escapes you; afterward, close the reference and reproduce it yourself.

## 11. Mistakes to watch for

- Confusing `products` (**collection**) with `product` (**one record**).
- Reversing the left-hand **destination** and right-hand **value**.
- Using `==` when assignment `=` is needed.
- Using `+=` for dictionary insertion.
- Assuming `[]` and `.get()` behave identically for missing keys.
- Forgetting that assigning an existing key **overwrites its value**.
- Assuming a correct return value proves that the original dictionary was mutated.

## 12. Tomorrow's exact restart point

1. Open `inventory.py` and check that the current `create_product()` matches the intended basic structure.
2. Independently write `test_create_product()` in `test_inventory.py`:
   - Start with `products = {}`.
   - Call `create_product()` with ID `101`, name `"Keyboard"`, price `49.99`, and quantity `20`.
   - Assert `101 in products`.
   - Assert `products[101]["name"] == "Keyboard"`.
3. Run `pytest` and debug any failures.
4. Add input validation **one rule at a time**, with a test for each rejected input.
5. For every insertion or update, deliberately identify the **collection, key, and value**.

## 13. Optional 10-minute review

Without looking at the examples first, open a scratch Python file and:

1. Create an inventory dictionary with one product.
2. Check whether product ID `101` exists.
3. Safely retrieve product ID `999`.
4. Add a new product with ID `102`.
5. Change product `101`'s quantity.
6. Retrieve the changed quantity and print the inventory.

If stuck, consult Section 3, close the notes, and write the statement again from memory.

**Don't turn this into a long study session.** The objective is short retrieval practice followed by real implementation in Inventory API.
