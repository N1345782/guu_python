"""
Задача 05-13. Соседние равные

Прочитайте числа через пробел и выведите True, если в списке есть два
соседних равных элемента, иначе False.

Пример
------
Ввод:
1 2 2 3
Вывод:
True
"""

# TODO: переберите соседние пары (a[i] и a[i+1]) и сравните

nums = [int(x) for x in input().split()]

found = False
for i in range(len(nums) - 1):
    if nums[i] == nums[i + 1]:
        found = True
        break

print(found)