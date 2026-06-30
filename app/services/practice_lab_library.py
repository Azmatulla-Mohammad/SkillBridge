from __future__ import annotations

import json
from typing import Any


def q(
    *,
    title: str,
    companies: list[str],
    frequency: str,
    problem: str,
    input_format: str,
    output_format: str,
    constraints: str,
    sample_input: str,
    sample_output: str,
    explanation: str,
    starter_code: str,
    reference_solution: str,
    hints: list[str],
    time_complexity: str,
    space_complexity: str,
) -> dict[str, Any]:
    return {
        "title": title,
        "companies": companies,
        "frequency": frequency,
        "problem": problem,
        "input_format": input_format,
        "output_format": output_format,
        "constraints": constraints,
        "sample_input": sample_input,
        "sample_output": sample_output,
        "explanation": explanation,
        "starter_code": starter_code.strip() + "\n",
        "reference_solution": reference_solution.strip() + "\n",
        "hints": hints,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
    }


INTERVIEW_LIBRARY: list[dict[str, Any]] = [
    {
        "topic_name": "Variables & Input Output",
        "questions": [
            q(
                title="Swap Two Values Without Temporary Variable",
                companies=["TCS", "Infosys", "Accenture", "Deloitte"],
                frequency="High",
                problem="Read two integers and print them after swapping their values without using a third variable.",
                input_format="Two integers a and b on one line.",
                output_format="Print the swapped values separated by a space.",
                constraints="-10^9 <= a, b <= 10^9",
                sample_input="7 12",
                sample_output="12 7",
                explanation="The values 7 and 12 exchange positions, so the output is 12 followed by 7.",
                starter_code="""
a, b = map(int, input().split())

# Write your solution below
""",
                reference_solution="""
a, b = map(int, input().split())
a, b = b, a
print(a, b)
""",
                hints=["Python supports tuple unpacking.", "Assign both variables in one statement."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Convert Minutes to Hours and Minutes",
                companies=["Amazon", "Zoho", "Freshworks", "Startup"],
                frequency="Medium",
                problem="Given a total number of minutes, convert it into complete hours and remaining minutes.",
                input_format="One integer total_minutes.",
                output_format="Print hours and minutes separated by a space.",
                constraints="0 <= total_minutes <= 100000",
                sample_input="135",
                sample_output="2 15",
                explanation="135 minutes contains 2 complete hours and 15 remaining minutes.",
                starter_code="""
total_minutes = int(input())

# Write your solution below
""",
                reference_solution="""
total_minutes = int(input())
hours = total_minutes // 60
minutes = total_minutes % 60
print(hours, minutes)
""",
                hints=["Integer division gives complete hours.", "Modulo gives the remaining minutes."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Calculate Simple Interest",
                companies=["Infosys", "Wipro", "HCL", "Capgemini"],
                frequency="High",
                problem="Read principal, annual rate, and time in years. Print the simple interest amount.",
                input_format="Three numbers p, r, and t on one line.",
                output_format="Print the simple interest rounded to two decimal places.",
                constraints="0 <= p <= 10^7, 0 <= r <= 100, 0 <= t <= 100",
                sample_input="1000 5 2",
                sample_output="100.00",
                explanation="Simple interest is p * r * t / 100, so 1000 * 5 * 2 / 100 = 100.",
                starter_code="""
p, r, t = map(float, input().split())

# Write your solution below
""",
                reference_solution="""
p, r, t = map(float, input().split())
interest = (p * r * t) / 100
print(f"{interest:.2f}")
""",
                hints=["Use the formula p * r * t / 100.", "Use formatted output for two decimals."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Format Candidate Score",
                companies=["Deloitte", "Accenture", "Cognizant", "Tech Mahindra"],
                frequency="Medium",
                problem="Read a candidate name and score, then print a short formatted interview result line.",
                input_format="First line contains the candidate name. Second line contains an integer score.",
                output_format="Print: name scored score marks",
                constraints="1 <= length of name <= 50, 0 <= score <= 100",
                sample_input="Anita\n86",
                sample_output="Anita scored 86 marks",
                explanation="The name and score are inserted into the required sentence.",
                starter_code="""
name = input()
score = int(input())

# Write your solution below
""",
                reference_solution="""
name = input()
score = int(input())
print(f"{name} scored {score} marks")
""",
                hints=["Read the two inputs separately.", "Use an f-string or string concatenation."],
                time_complexity="O(n), where n is the name length",
                space_complexity="O(n)",
            ),
            q(
                title="Find Last Digit of a Number",
                companies=["TCS", "Zoho", "Oracle", "Startup"],
                frequency="High",
                problem="Read an integer and print its last digit. The number may be negative.",
                input_format="One integer n.",
                output_format="Print one digit from 0 to 9.",
                constraints="-10^18 <= n <= 10^18",
                sample_input="-457",
                sample_output="7",
                explanation="The absolute value is 457, and its last digit is 7.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
print(abs(n) % 10)
""",
                hints=["Ignore the sign before taking the last digit.", "Use modulo 10."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Strings",
        "questions": [
            q(
                title="Reverse a String",
                companies=["Amazon", "Microsoft", "TCS", "Startup"],
                frequency="Very High",
                problem="Read a string and print the characters in reverse order.",
                input_format="One string text.",
                output_format="Print the reversed string.",
                constraints="0 <= length of text <= 100000",
                sample_input="skill",
                sample_output="lliks",
                explanation="The last character becomes first and the first character becomes last.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
print(text[::-1])
""",
                hints=["String slicing can move from right to left.", "A loop with reversed characters also works."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Check Palindrome Text",
                companies=["Google", "Amazon", "Zoho", "Freshworks"],
                frequency="Very High",
                problem="Check whether the given text reads the same from left to right and right to left.",
                input_format="One string text.",
                output_format="Print YES if it is a palindrome, otherwise print NO.",
                constraints="0 <= length of text <= 100000",
                sample_input="level",
                sample_output="YES",
                explanation="The word level is unchanged when reversed.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
print("YES" if text == text[::-1] else "NO")
""",
                hints=["Compare the string with its reverse.", "Keep the output exactly YES or NO."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Count Vowels in Text",
                companies=["Infosys", "Accenture", "Deloitte", "Startup"],
                frequency="High",
                problem="Count how many vowels appear in the input text. Treat uppercase and lowercase vowels equally.",
                input_format="One string text.",
                output_format="Print the vowel count.",
                constraints="0 <= length of text <= 100000",
                sample_input="Interview",
                sample_output="4",
                explanation="The vowels are I, e, i, and e.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
vowels = set("aeiou")
count = 0
for ch in text.lower():
    if ch in vowels:
        count += 1
print(count)
""",
                hints=["Convert characters to lowercase.", "Check membership in a vowel set."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Count Words in a Sentence",
                companies=["TCS", "Cognizant", "HCL", "Wipro"],
                frequency="High",
                problem="Read a sentence and count how many words it contains. Words are separated by spaces.",
                input_format="One line sentence.",
                output_format="Print the number of words.",
                constraints="0 <= length of sentence <= 100000",
                sample_input="coding interviews need practice",
                sample_output="4",
                explanation="The sentence has four space-separated words.",
                starter_code="""
sentence = input()

# Write your solution below
""",
                reference_solution="""
sentence = input()
words = sentence.split()
print(len(words))
""",
                hints=["split() ignores repeated spaces.", "The answer is the length of the word list."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Remove All Spaces",
                companies=["Zoho", "Freshworks", "Oracle", "Startup"],
                frequency="High",
                problem="Remove every space character from the given line and print the compact text.",
                input_format="One line text.",
                output_format="Print the text without spaces.",
                constraints="0 <= length of text <= 100000",
                sample_input="a b  c",
                sample_output="abc",
                explanation="All spaces are skipped while keeping the original order of other characters.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
result = []
for ch in text:
    if ch != " ":
        result.append(ch)
print("".join(result))
""",
                hints=["Build a new string or list.", "Skip characters that are exactly a space."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Most Frequent Character",
                companies=["Amazon", "Microsoft", "Adobe", "Startup"],
                frequency="High",
                problem="Find the character that appears most often in the input. If there is a tie, print the one that appears first.",
                input_format="One non-empty string text.",
                output_format="Print the most frequent character.",
                constraints="1 <= length of text <= 100000",
                sample_input="banana",
                sample_output="a",
                explanation="a appears three times, more than b or n.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
counts = {}
best = text[0]
for ch in text:
    counts[ch] = counts.get(ch, 0) + 1
    if counts[ch] > counts[best]:
        best = ch
print(best)
""",
                hints=["Track counts in a dictionary.", "Update the best character only when the count becomes larger."],
                time_complexity="O(n)",
                space_complexity="O(k), where k is the number of distinct characters",
            ),
            q(
                title="Check Two Words Are Anagrams",
                companies=["Google", "Microsoft", "Amazon", "Flipkart"],
                frequency="Very High",
                problem="Read two words and check whether both words contain the same characters with the same counts.",
                input_format="First line contains word a. Second line contains word b.",
                output_format="Print YES if they are anagrams, otherwise print NO.",
                constraints="1 <= length of each word <= 100000",
                sample_input="listen\nsilent",
                sample_output="YES",
                explanation="Both words contain the same letters with the same frequencies.",
                starter_code="""
a = input()
b = input()

# Write your solution below
""",
                reference_solution="""
a = input()
b = input()
print("YES" if sorted(a) == sorted(b) else "NO")
""",
                hints=["Character counts must match.", "Sorting both words is a simple way to compare."],
                time_complexity="O(n log n)",
                space_complexity="O(n)",
            ),
            q(
                title="Find Longest Word",
                companies=["Deloitte", "Infosys", "Capgemini", "Startup"],
                frequency="Medium",
                problem="Read a sentence and print the longest word. If multiple words share the maximum length, print the first one.",
                input_format="One sentence.",
                output_format="Print one word.",
                constraints="1 <= length of sentence <= 100000",
                sample_input="build clean readable solutions",
                sample_output="solutions",
                explanation="solutions has the largest length among the words.",
                starter_code="""
sentence = input()

# Write your solution below
""",
                reference_solution="""
sentence = input()
words = sentence.split()
best = words[0]
for word in words:
    if len(word) > len(best):
        best = word
print(best)
""",
                hints=["Split the sentence into words.", "Keep the first word when lengths are equal."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Toggle Character Case",
                companies=["Zoho", "Freshworks", "Paytm", "Startup"],
                frequency="Medium",
                problem="Convert lowercase letters to uppercase and uppercase letters to lowercase. Leave other characters unchanged.",
                input_format="One string text.",
                output_format="Print the case-toggled string.",
                constraints="0 <= length of text <= 100000",
                sample_input="PyThon3",
                sample_output="pYtHON3",
                explanation="Each alphabetic character changes case, while 3 remains unchanged.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
print(text.swapcase())
""",
                hints=["Python strings have case helper methods.", "Non-letters should be copied unchanged."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="First Non-Repeating Character",
                companies=["Amazon", "Adobe", "Microsoft", "Razorpay"],
                frequency="High",
                problem="Find the first character in the string that appears exactly once.",
                input_format="One string text.",
                output_format="Print the first non-repeating character, or -1 if no such character exists.",
                constraints="1 <= length of text <= 100000",
                sample_input="swiss",
                sample_output="w",
                explanation="s appears more than once, and w is the first character with frequency one.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
counts = {}
for ch in text:
    counts[ch] = counts.get(ch, 0) + 1
answer = "-1"
for ch in text:
    if counts[ch] == 1:
        answer = ch
        break
print(answer)
""",
                hints=["Count every character first.", "Scan the original string again to preserve order."],
                time_complexity="O(n)",
                space_complexity="O(k)",
            ),
        ],
    },
    {
        "topic_name": "Lists",
        "questions": [
            q(
                title="Largest Element in List",
                companies=["TCS", "Infosys", "Amazon", "Startup"],
                frequency="Very High",
                problem="Read a list of integers and print the largest value.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the largest integer.",
                constraints="1 <= n <= 100000",
                sample_input="5\n4 9 1 7 2",
                sample_output="9",
                explanation="9 is greater than every other number in the list.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split()))

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split()))
largest = numbers[0]
for value in numbers:
    if value > largest:
        largest = value
print(largest)
""",
                hints=["Start with the first element as the current largest.", "Compare every element once."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Second Largest Distinct Number",
                companies=["Amazon", "Microsoft", "Flipkart", "Zoho"],
                frequency="Very High",
                problem="Find the second largest distinct number in the list.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the second largest distinct number, or -1 if it does not exist.",
                constraints="1 <= n <= 100000",
                sample_input="6\n10 5 10 8 2 8",
                sample_output="8",
                explanation="The distinct values are 10, 8, 5, and 2; the second largest is 8.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split()))

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split()))
first = None
second = None
for value in numbers:
    if first is None or value > first:
        if value != first:
            second = first
        first = value
    elif value != first and (second is None or value > second):
        second = value
print(second if second is not None else -1)
""",
                hints=["Track the largest and second largest separately.", "Ignore duplicates of the largest value."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Remove Duplicate Numbers Preserve Order",
                companies=["Zoho", "Freshworks", "Paytm", "Startup"],
                frequency="High",
                problem="Remove duplicate integers while keeping the first occurrence of each number.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the remaining integers separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="7\n3 5 3 2 5 8 2",
                sample_output="3 5 2 8",
                explanation="Only the first appearance of every value is kept.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
seen = set()
result = []
for value in numbers:
    if value not in seen:
        seen.add(value)
        result.append(value)
print(*result)
""",
                hints=["A set can remember values already printed.", "Append a number only the first time it appears."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Rotate List Right by One",
                companies=["Microsoft", "TCS", "Cognizant", "Startup"],
                frequency="High",
                problem="Move the last element of the list to the front and shift all other elements one position right.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the rotated list separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="5\n1 2 3 4 5",
                sample_output="5 1 2 3 4",
                explanation="The last value 5 becomes the first value.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
if n > 0:
    numbers = [numbers[-1]] + numbers[:-1]
print(*numbers)
""",
                hints=["Handle the empty list separately.", "Use the last element and all elements before it."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Merge Two Sorted Lists",
                companies=["Google", "Amazon", "Microsoft", "Flipkart"],
                frequency="Very High",
                problem="Merge two individually sorted integer lists into one sorted list.",
                input_format="Line 1 contains n. Line 2 contains n sorted integers. Line 3 contains m. Line 4 contains m sorted integers.",
                output_format="Print the merged sorted values separated by spaces.",
                constraints="0 <= n, m <= 100000",
                sample_input="3\n1 4 7\n4\n2 3 6 8",
                sample_output="1 2 3 4 6 7 8",
                explanation="The output contains every number from both lists in sorted order.",
                starter_code="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []
i = j = 0
merged = []
while i < n and j < m:
    if a[i] <= b[j]:
        merged.append(a[i])
        i += 1
    else:
        merged.append(b[j])
        j += 1
merged.extend(a[i:])
merged.extend(b[j:])
print(*merged)
""",
                hints=["Use two pointers.", "Append the smaller current value and advance that pointer."],
                time_complexity="O(n + m)",
                space_complexity="O(n + m)",
            ),
            q(
                title="Missing Number from 1 to N",
                companies=["Amazon", "Adobe", "Oracle", "Razorpay"],
                frequency="High",
                problem="Numbers from 1 to n are expected, but one number is missing. Find the missing value.",
                input_format="First line contains n. Second line contains n - 1 integers.",
                output_format="Print the missing number.",
                constraints="2 <= n <= 100000",
                sample_input="5\n1 2 4 5",
                sample_output="3",
                explanation="The number 3 is absent from the sequence 1 through 5.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split()))

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split()))
expected = n * (n + 1) // 2
print(expected - sum(numbers))
""",
                hints=["Use the sum of the first n natural numbers.", "Subtract the actual sum from the expected sum."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Count Even and Odd Numbers",
                companies=["Infosys", "Wipro", "Tech Mahindra", "Startup"],
                frequency="High",
                problem="Count how many values in the list are even and how many are odd.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print even_count and odd_count separated by a space.",
                constraints="0 <= n <= 100000",
                sample_input="6\n1 2 3 4 5 8",
                sample_output="3 3",
                explanation="2, 4, and 8 are even; 1, 3, and 5 are odd.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
even = 0
odd = 0
for value in numbers:
    if value % 2 == 0:
        even += 1
    else:
        odd += 1
print(even, odd)
""",
                hints=["Use modulo 2.", "Maintain two counters."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Move Zeros to End",
                companies=["Microsoft", "Google", "PhonePe", "Meesho"],
                frequency="High",
                problem="Rearrange the list so that all zero values move to the end while non-zero values keep their relative order.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the rearranged list separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="7\n0 3 0 1 5 0 2",
                sample_output="3 1 5 2 0 0 0",
                explanation="The non-zero values stay in order, followed by all zeros.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
result = []
zero_count = 0
for value in numbers:
    if value == 0:
        zero_count += 1
    else:
        result.append(value)
result.extend([0] * zero_count)
print(*result)
""",
                hints=["Collect non-zero values first.", "Count zeros and append them at the end."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
        ],
    },
    {
        "topic_name": "Tuples",
        "questions": [
            q(
                title="Swap Pair Tuple",
                companies=["TCS", "Infosys", "Zoho", "Startup"],
                frequency="Medium",
                problem="Read two values, store them as a tuple pair, and print a new tuple with the values swapped.",
                input_format="Two space-separated strings.",
                output_format="Print the swapped tuple using Python tuple format.",
                constraints="Each value length is between 1 and 30.",
                sample_input="red blue",
                sample_output="('blue', 'red')",
                explanation="The tuple ('red', 'blue') becomes ('blue', 'red').",
                starter_code="""
a, b = input().split()

# Write your solution below
""",
                reference_solution="""
a, b = input().split()
pair = (a, b)
swapped = (pair[1], pair[0])
print(swapped)
""",
                hints=["Tuple values can be accessed by index.", "Create a new tuple in the swapped order."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Count Tuple Occurrences",
                companies=["Accenture", "Deloitte", "Cognizant", "Startup"],
                frequency="Medium",
                problem="Read tuple values and a target value. Count how many times the target appears.",
                input_format="First line contains n. Second line contains n integers. Third line contains target.",
                output_format="Print the target frequency.",
                constraints="0 <= n <= 100000",
                sample_input="6\n2 4 2 5 2 7\n2",
                sample_output="3",
                explanation="The value 2 appears three times in the tuple.",
                starter_code="""
n = int(input())
values = tuple(map(int, input().split())) if n else tuple()
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
values = tuple(map(int, input().split())) if n else tuple()
target = int(input())
print(values.count(target))
""",
                hints=["Tuples support count().", "A manual loop with a counter also works."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Find Minimum and Maximum in Tuple",
                companies=["Infosys", "Wipro", "HCL", "Capgemini"],
                frequency="Medium",
                problem="Read integers into a tuple and print the smallest and largest values.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print minimum and maximum separated by a space.",
                constraints="1 <= n <= 100000",
                sample_input="5\n9 3 12 4 7",
                sample_output="3 12",
                explanation="3 is the smallest value and 12 is the largest value.",
                starter_code="""
n = int(input())
values = tuple(map(int, input().split()))

# Write your solution below
""",
                reference_solution="""
n = int(input())
values = tuple(map(int, input().split()))
print(min(values), max(values))
""",
                hints=["Use min and max, or scan the tuple once.", "Print both values on one line."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
        ],
    },
    {
        "topic_name": "Dictionary",
        "questions": [
            q(
                title="Word Frequency Counter",
                companies=["Amazon", "Google", "Deloitte", "Startup"],
                frequency="High",
                problem="Count the frequency of each word in a sentence and print one word-count pair per line in first-seen order.",
                input_format="One sentence.",
                output_format="For each distinct word, print word and count separated by a space.",
                constraints="1 <= length of sentence <= 100000",
                sample_input="data code data test code data",
                sample_output="data 3\ncode 2\ntest 1",
                explanation="Words are counted as they appear, and first-seen order is preserved.",
                starter_code="""
sentence = input()

# Write your solution below
""",
                reference_solution="""
sentence = input()
counts = {}
order = []
for word in sentence.split():
    if word not in counts:
        counts[word] = 0
        order.append(word)
    counts[word] += 1
for word in order:
    print(word, counts[word])
""",
                hints=["Use a dictionary for counts.", "Keep an order list for first appearances."],
                time_complexity="O(n)",
                space_complexity="O(k)",
            ),
            q(
                title="Character Count Dictionary",
                companies=["Zoho", "Freshworks", "Microsoft", "Startup"],
                frequency="High",
                problem="Build a dictionary of character counts for the given string and print the dictionary.",
                input_format="One string text.",
                output_format="Print a Python dictionary mapping each character to its count.",
                constraints="0 <= length of text <= 100000",
                sample_input="aba",
                sample_output="{'a': 2, 'b': 1}",
                explanation="a appears twice and b appears once.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
counts = {}
for ch in text:
    counts[ch] = counts.get(ch, 0) + 1
print(counts)
""",
                hints=["Use get(key, 0) to handle new characters.", "Dictionaries preserve insertion order in modern Python."],
                time_complexity="O(n)",
                space_complexity="O(k)",
            ),
            q(
                title="Merge Marks Dictionaries",
                companies=["Oracle", "Infosys", "Accenture", "Startup"],
                frequency="Medium",
                problem="Read two student-mark dictionaries and merge them. If a student appears in both, keep the higher mark.",
                input_format="First line n, followed by n lines of name mark. Then line m, followed by m lines of name mark.",
                output_format="Print each student and final mark in insertion order.",
                constraints="0 <= n, m <= 1000, 0 <= mark <= 100",
                sample_input="2\nAsha 80\nRavi 75\n2\nRavi 82\nMaya 91",
                sample_output="Asha 80\nRavi 82\nMaya 91",
                explanation="Ravi appears twice, so the higher mark 82 is kept.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
marks = {}
order = []
for _ in range(n):
    name, score = input().split()
    marks[name] = int(score)
    order.append(name)
m = int(input())
for _ in range(m):
    name, score = input().split()
    score = int(score)
    if name not in marks:
        order.append(name)
        marks[name] = score
    else:
        marks[name] = max(marks[name], score)
for name in order:
    print(name, marks[name])
""",
                hints=["Track names in insertion order.", "Use max when a duplicate name appears."],
                time_complexity="O(n + m)",
                space_complexity="O(n + m)",
            ),
            q(
                title="Student with Highest Marks",
                companies=["TCS", "Cognizant", "Deloitte", "Capgemini"],
                frequency="High",
                problem="Read student names and marks, then print the name of the student with the highest mark. If tied, print the first one.",
                input_format="First line contains n. Next n lines contain name and mark.",
                output_format="Print the top student's name.",
                constraints="1 <= n <= 100000, 0 <= mark <= 100",
                sample_input="3\nAsha 88\nRavi 91\nMaya 91",
                sample_output="Ravi",
                explanation="Ravi and Maya both have 91, but Ravi appears first.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
best_name = ""
best_score = -1
for _ in range(n):
    name, score = input().split()
    score = int(score)
    if score > best_score:
        best_score = score
        best_name = name
print(best_name)
""",
                hints=["Update the answer only when the score is strictly higher.", "Do not replace the first student in a tie."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Invert Key Value Mapping",
                companies=["Adobe", "Oracle", "Freshworks", "Startup"],
                frequency="Medium",
                problem="Read key-value pairs where all values are unique. Create a new dictionary where values become keys and keys become values.",
                input_format="First line contains n. Next n lines contain key value.",
                output_format="Print the inverted dictionary.",
                constraints="0 <= n <= 1000, keys and values contain no spaces",
                sample_input="2\none 1\ntwo 2",
                sample_output="{'1': 'one', '2': 'two'}",
                explanation="The value 1 maps back to one and 2 maps back to two.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
data = {}
for _ in range(n):
    key, value = input().split()
    data[key] = value
inverted = {}
for key, value in data.items():
    inverted[value] = key
print(inverted)
""",
                hints=["Loop over dictionary items.", "Assign inverted[value] = key."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
        ],
    },
    {
        "topic_name": "Sets",
        "questions": [
            q(
                title="Common Elements Between Lists",
                companies=["Amazon", "Google", "Zoho", "Startup"],
                frequency="High",
                problem="Find all values that appear in both lists and print them in sorted order.",
                input_format="Line 1 contains n. Line 2 contains n integers. Line 3 contains m. Line 4 contains m integers.",
                output_format="Print common values separated by spaces.",
                constraints="0 <= n, m <= 100000",
                sample_input="5\n4 1 3 2 4\n4\n6 2 4 8",
                sample_output="2 4",
                explanation="Only 2 and 4 are present in both lists.",
                starter_code="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []
common = sorted(set(a) & set(b))
print(*common)
""",
                hints=["Convert both lists to sets.", "Use set intersection."],
                time_complexity="O(n + m + k log k)",
                space_complexity="O(n + m)",
            ),
            q(
                title="Unique Sorted Numbers",
                companies=["Infosys", "Wipro", "Accenture", "Startup"],
                frequency="High",
                problem="Remove duplicate numbers and print the remaining values in ascending order.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print unique sorted numbers separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="8\n5 3 5 1 2 3 4 1",
                sample_output="1 2 3 4 5",
                explanation="Duplicates are removed and the result is sorted.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
print(*sorted(set(numbers)))
""",
                hints=["A set stores unique values.", "Sort the set before printing."],
                time_complexity="O(n log n)",
                space_complexity="O(n)",
            ),
            q(
                title="Check Subset Relation",
                companies=["Microsoft", "Oracle", "Deloitte", "Startup"],
                frequency="Medium",
                problem="Check whether every value from the first list is present in the second list.",
                input_format="Line 1 contains n. Line 2 contains n integers. Line 3 contains m. Line 4 contains m integers.",
                output_format="Print YES if the first list is a subset of the second, otherwise print NO.",
                constraints="0 <= n, m <= 100000",
                sample_input="3\n1 2 2\n5\n5 1 4 2 3",
                sample_output="YES",
                explanation="The unique values 1 and 2 from the first list are present in the second list.",
                starter_code="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
a = list(map(int, input().split())) if n else []
m = int(input())
b = list(map(int, input().split())) if m else []
print("YES" if set(a).issubset(set(b)) else "NO")
""",
                hints=["Only unique membership matters.", "Use issubset or compare set differences."],
                time_complexity="O(n + m)",
                space_complexity="O(n + m)",
            ),
        ],
    },
    {
        "topic_name": "Loops",
        "questions": [
            q(
                title="Print Numbers from 1 to N",
                companies=["TCS", "Infosys", "Wipro", "HCL"],
                frequency="High",
                problem="Read n and print all numbers from 1 to n on one line.",
                input_format="One integer n.",
                output_format="Print numbers from 1 to n separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="5",
                sample_output="1 2 3 4 5",
                explanation="The sequence starts at 1 and stops at n.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for value in range(1, n + 1):
    print(value, end=" ")
""",
                hints=["Use range(1, n + 1).", "Print each number with a space ending."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Sum of Digits",
                companies=["Zoho", "Freshworks", "TCS", "Startup"],
                frequency="Very High",
                problem="Read an integer and calculate the sum of its digits.",
                input_format="One integer n.",
                output_format="Print the digit sum.",
                constraints="-10^18 <= n <= 10^18",
                sample_input="5029",
                sample_output="16",
                explanation="5 + 0 + 2 + 9 = 16.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = abs(int(input()))
total = 0
if n == 0:
    total = 0
while n > 0:
    total += n % 10
    n //= 10
print(total)
""",
                hints=["Use modulo 10 to get the last digit.", "Use integer division to remove the last digit."],
                time_complexity="O(d), where d is the number of digits",
                space_complexity="O(1)",
            ),
            q(
                title="Reverse a Number",
                companies=["Infosys", "Accenture", "Zoho", "Startup"],
                frequency="High",
                problem="Read an integer and print the number formed by reversing its digits. Preserve a negative sign.",
                input_format="One integer n.",
                output_format="Print the reversed integer.",
                constraints="-10^18 <= n <= 10^18",
                sample_input="-120",
                sample_output="-21",
                explanation="The digits 120 reverse to 021, which is 21, and the sign remains negative.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
sign = -1 if n < 0 else 1
n = abs(n)
rev = 0
while n > 0:
    rev = rev * 10 + n % 10
    n //= 10
print(sign * rev)
""",
                hints=["Track the sign separately.", "Build the reversed number one digit at a time."],
                time_complexity="O(d)",
                space_complexity="O(1)",
            ),
            q(
                title="Count Digits",
                companies=["TCS", "Cognizant", "Capgemini", "Startup"],
                frequency="High",
                problem="Count the number of digits in the given integer.",
                input_format="One integer n.",
                output_format="Print the digit count.",
                constraints="-10^18 <= n <= 10^18",
                sample_input="7005",
                sample_output="4",
                explanation="7005 has four digits.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = abs(int(input()))
if n == 0:
    print(1)
else:
    count = 0
    while n > 0:
        count += 1
        n //= 10
    print(count)
""",
                hints=["Zero has one digit.", "Repeatedly divide by 10."],
                time_complexity="O(d)",
                space_complexity="O(1)",
            ),
            q(
                title="Multiplication Table",
                companies=["Infosys", "Wipro", "Tech Mahindra", "Startup"],
                frequency="Medium",
                problem="Print the first ten multiples of a number.",
                input_format="One integer n.",
                output_format="Print each line in the format n x i = result for i from 1 to 10.",
                constraints="-100000 <= n <= 100000",
                sample_input="3",
                sample_output="3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15\n3 x 6 = 18\n3 x 7 = 21\n3 x 8 = 24\n3 x 9 = 27\n3 x 10 = 30",
                explanation="Each line multiplies 3 by the current counter.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(1, 11):
    print(f"{n} x {i} = {n * i}")
""",
                hints=["Use a loop from 1 to 10.", "Use formatted strings for the exact output."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Find Divisors of a Number",
                companies=["Oracle", "Zoho", "HCL", "Startup"],
                frequency="Medium",
                problem="Print all positive divisors of the given number in increasing order.",
                input_format="One positive integer n.",
                output_format="Print divisors separated by spaces.",
                constraints="1 <= n <= 100000",
                sample_input="12",
                sample_output="1 2 3 4 6 12",
                explanation="Each printed value divides 12 with no remainder.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for value in range(1, n + 1):
    if n % value == 0:
        print(value, end=" ")
""",
                hints=["A divisor leaves remainder zero.", "Check every value from 1 to n for the easy version."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Functions",
        "questions": [
            q(
                title="Function to Check Even Number",
                companies=["TCS", "Infosys", "Accenture", "Startup"],
                frequency="High",
                problem="Write a function that returns True if a number is even, otherwise False.",
                input_format="One integer n.",
                output_format="Print True or False.",
                constraints="-10^9 <= n <= 10^9",
                sample_input="24",
                sample_output="True",
                explanation="24 is divisible by 2, so the function returns True.",
                starter_code="""
n = int(input())

def is_even(number):
    # Write your solution below
    pass

print(is_even(n))
""",
                reference_solution="""
n = int(input())

def is_even(number):
    return number % 2 == 0

print(is_even(n))
""",
                hints=["Use modulo 2.", "Return a boolean value from the function."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Function to Find Maximum of Three",
                companies=["Deloitte", "Capgemini", "Cognizant", "Startup"],
                frequency="Medium",
                problem="Write a function that returns the largest of three integers.",
                input_format="Three integers on one line.",
                output_format="Print the largest integer.",
                constraints="-10^9 <= values <= 10^9",
                sample_input="4 11 9",
                sample_output="11",
                explanation="11 is greater than 4 and 9.",
                starter_code="""
a, b, c = map(int, input().split())

def maximum_of_three(x, y, z):
    # Write your solution below
    pass

print(maximum_of_three(a, b, c))
""",
                reference_solution="""
a, b, c = map(int, input().split())

def maximum_of_three(x, y, z):
    largest = x
    if y > largest:
        largest = y
    if z > largest:
        largest = z
    return largest

print(maximum_of_three(a, b, c))
""",
                hints=["Start with one value as largest.", "Compare the other two values."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Function to Find GCD",
                companies=["Amazon", "Microsoft", "Oracle", "Zoho"],
                frequency="High",
                problem="Write a function that returns the greatest common divisor of two positive integers.",
                input_format="Two positive integers a and b.",
                output_format="Print the GCD.",
                constraints="1 <= a, b <= 10^9",
                sample_input="18 24",
                sample_output="6",
                explanation="6 is the largest number that divides both 18 and 24.",
                starter_code="""
a, b = map(int, input().split())

def gcd(x, y):
    # Write your solution below
    pass

print(gcd(a, b))
""",
                reference_solution="""
a, b = map(int, input().split())

def gcd(x, y):
    while y:
        x, y = y, x % y
    return x

print(gcd(a, b))
""",
                hints=["Use the Euclidean algorithm.", "Keep replacing x and y until the remainder is zero."],
                time_complexity="O(log min(a, b))",
                space_complexity="O(1)",
            ),
            q(
                title="Function to Count Vowels",
                companies=["Infosys", "Freshworks", "Deloitte", "Startup"],
                frequency="Medium",
                problem="Write a function that returns the number of vowels in a string.",
                input_format="One string text.",
                output_format="Print the vowel count.",
                constraints="0 <= length of text <= 100000",
                sample_input="Function",
                sample_output="3",
                explanation="u, i, and o are vowels.",
                starter_code="""
text = input()

def count_vowels(value):
    # Write your solution below
    pass

print(count_vowels(text))
""",
                reference_solution="""
text = input()

def count_vowels(value):
    vowels = set("aeiou")
    count = 0
    for ch in value.lower():
        if ch in vowels:
            count += 1
    return count

print(count_vowels(text))
""",
                hints=["Convert the input to lowercase.", "Use a set for vowel lookup."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Function to Return Second Largest",
                companies=["Google", "Amazon", "Flipkart", "Startup"],
                frequency="High",
                problem="Write a function that returns the second largest distinct number in a list.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the second largest distinct number, or -1 if missing.",
                constraints="1 <= n <= 100000",
                sample_input="5\n4 1 7 7 3",
                sample_output="4",
                explanation="The distinct values are 7, 4, 3, and 1.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split()))

def second_largest(values):
    # Write your solution below
    pass

print(second_largest(numbers))
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split()))

def second_largest(values):
    unique_values = sorted(set(values), reverse=True)
    return unique_values[1] if len(unique_values) >= 2 else -1

print(second_largest(numbers))
""",
                hints=["Distinct values matter.", "Sorting unique values is acceptable for this easy version."],
                time_complexity="O(n log n)",
                space_complexity="O(n)",
            ),
            q(
                title="Function to Convert Celsius to Fahrenheit",
                companies=["TCS", "HCL", "Wipro", "Startup"],
                frequency="Medium",
                problem="Write a function that converts a Celsius temperature to Fahrenheit.",
                input_format="One number celsius.",
                output_format="Print the Fahrenheit value rounded to two decimal places.",
                constraints="-273.15 <= celsius <= 100000",
                sample_input="37",
                sample_output="98.60",
                explanation="37 Celsius converts to 98.6 Fahrenheit.",
                starter_code="""
celsius = float(input())

def to_fahrenheit(value):
    # Write your solution below
    pass

print(f"{to_fahrenheit(celsius):.2f}")
""",
                reference_solution="""
celsius = float(input())

def to_fahrenheit(value):
    return value * 9 / 5 + 32

print(f"{to_fahrenheit(celsius):.2f}")
""",
                hints=["Use the formula C * 9 / 5 + 32.", "Return the converted value from the function."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Recursion",
        "questions": [
            q(
                title="Recursive Factorial",
                companies=["Amazon", "Microsoft", "TCS", "Startup"],
                frequency="High",
                problem="Use recursion to calculate n factorial.",
                input_format="One integer n.",
                output_format="Print n!.",
                constraints="0 <= n <= 12",
                sample_input="5",
                sample_output="120",
                explanation="5! = 5 * 4 * 3 * 2 * 1 = 120.",
                starter_code="""
n = int(input())

def factorial(value):
    # Write your solution below
    pass

print(factorial(n))
""",
                reference_solution="""
n = int(input())

def factorial(value):
    if value <= 1:
        return 1
    return value * factorial(value - 1)

print(factorial(n))
""",
                hints=["Identify the base case for 0 and 1.", "Reduce the problem by calling factorial(n - 1)."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Recursive Fibonacci Number",
                companies=["Infosys", "Wipro", "Deloitte", "Startup"],
                frequency="Medium",
                problem="Use recursion to print the nth Fibonacci number where F0 = 0 and F1 = 1.",
                input_format="One integer n.",
                output_format="Print Fn.",
                constraints="0 <= n <= 25",
                sample_input="7",
                sample_output="13",
                explanation="The sequence is 0, 1, 1, 2, 3, 5, 8, 13.",
                starter_code="""
n = int(input())

def fibonacci(value):
    # Write your solution below
    pass

print(fibonacci(n))
""",
                reference_solution="""
n = int(input())

def fibonacci(value):
    if value <= 1:
        return value
    return fibonacci(value - 1) + fibonacci(value - 2)

print(fibonacci(n))
""",
                hints=["F0 is 0 and F1 is 1.", "Every later value is the sum of the previous two."],
                time_complexity="O(2^n)",
                space_complexity="O(n)",
            ),
            q(
                title="Recursive Sum of Natural Numbers",
                companies=["TCS", "Capgemini", "Cognizant", "Startup"],
                frequency="Medium",
                problem="Use recursion to calculate the sum 1 + 2 + ... + n.",
                input_format="One integer n.",
                output_format="Print the sum.",
                constraints="0 <= n <= 1000",
                sample_input="5",
                sample_output="15",
                explanation="1 + 2 + 3 + 4 + 5 = 15.",
                starter_code="""
n = int(input())

def natural_sum(value):
    # Write your solution below
    pass

print(natural_sum(n))
""",
                reference_solution="""
n = int(input())

def natural_sum(value):
    if value == 0:
        return 0
    return value + natural_sum(value - 1)

print(natural_sum(n))
""",
                hints=["When n is 0, the sum is 0.", "Add n to the sum of n - 1."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Recursive Power Calculation",
                companies=["Oracle", "Zoho", "Adobe", "Startup"],
                frequency="Medium",
                problem="Use recursion to calculate base raised to a non-negative exponent.",
                input_format="Two integers base and exponent.",
                output_format="Print base^exponent.",
                constraints="-1000 <= base <= 1000, 0 <= exponent <= 20",
                sample_input="2 5",
                sample_output="32",
                explanation="2 multiplied by itself 5 times equals 32.",
                starter_code="""
base, exponent = map(int, input().split())

def power(x, n):
    # Write your solution below
    pass

print(power(base, exponent))
""",
                reference_solution="""
base, exponent = map(int, input().split())

def power(x, n):
    if n == 0:
        return 1
    return x * power(x, n - 1)

print(power(base, exponent))
""",
                hints=["Any number to the power 0 is 1.", "Multiply by base and reduce exponent by 1."],
                time_complexity="O(exponent)",
                space_complexity="O(exponent)",
            ),
        ],
    },
    {
        "topic_name": "Searching",
        "questions": [
            q(
                title="Linear Search Position",
                companies=["TCS", "Infosys", "Amazon", "Startup"],
                frequency="High",
                problem="Find the first position of a target value in a list using linear search.",
                input_format="First line contains n. Second line contains n integers. Third line contains target.",
                output_format="Print the zero-based index, or -1 if absent.",
                constraints="0 <= n <= 100000",
                sample_input="5\n4 8 1 8 9\n8",
                sample_output="1",
                explanation="The first 8 appears at index 1.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())
answer = -1
for index, value in enumerate(numbers):
    if value == target:
        answer = index
        break
print(answer)
""",
                hints=["Scan from left to right.", "Stop when the first match is found."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Binary Search Sorted List",
                companies=["Google", "Amazon", "Microsoft", "Flipkart"],
                frequency="Very High",
                problem="Search for a target in a sorted list using binary search.",
                input_format="First line contains n. Second line contains n sorted integers. Third line contains target.",
                output_format="Print the index if found, otherwise -1.",
                constraints="0 <= n <= 100000",
                sample_input="6\n2 4 7 10 15 20\n10",
                sample_output="3",
                explanation="10 is found at zero-based index 3.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())
left = 0
right = n - 1
answer = -1
while left <= right:
    mid = (left + right) // 2
    if numbers[mid] == target:
        answer = mid
        break
    if numbers[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
print(answer)
""",
                hints=["Compare with the middle element.", "Discard half of the search space each time."],
                time_complexity="O(log n)",
                space_complexity="O(1)",
            ),
            q(
                title="Count Occurrences of Target",
                companies=["Adobe", "Oracle", "Zoho", "Startup"],
                frequency="High",
                problem="Count how many times a target value appears in the list.",
                input_format="First line contains n. Second line contains n integers. Third line contains target.",
                output_format="Print the occurrence count.",
                constraints="0 <= n <= 100000",
                sample_input="7\n1 3 3 5 3 8 1\n3",
                sample_output="3",
                explanation="The target value 3 appears three times.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())
count = 0
for value in numbers:
    if value == target:
        count += 1
print(count)
""",
                hints=["Use a counter.", "Increase it whenever a value equals the target."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Find First Greater Element",
                companies=["PhonePe", "Razorpay", "Meesho", "Startup"],
                frequency="Medium",
                problem="Find the first list value that is greater than the given target.",
                input_format="First line contains n. Second line contains n integers. Third line contains target.",
                output_format="Print the first greater value, or -1 if no value is greater.",
                constraints="0 <= n <= 100000",
                sample_input="5\n2 4 9 3 10\n6",
                sample_output="9",
                explanation="9 is the first value encountered that is greater than 6.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())
answer = -1
for value in numbers:
    if value > target:
        answer = value
        break
print(answer)
""",
                hints=["Scan in original order.", "Break as soon as a greater value is found."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Sorting",
        "questions": [
            q(
                title="Bubble Sort Numbers",
                companies=["TCS", "Infosys", "Accenture", "Startup"],
                frequency="High",
                problem="Sort the list in ascending order using the bubble sort technique.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the sorted list separated by spaces.",
                constraints="0 <= n <= 1000",
                sample_input="5\n5 1 4 2 8",
                sample_output="1 2 4 5 8",
                explanation="Adjacent values are repeatedly swapped until the list becomes sorted.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
for i in range(n):
    for j in range(0, n - i - 1):
        if numbers[j] > numbers[j + 1]:
            numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
print(*numbers)
""",
                hints=["Compare adjacent values.", "Move the largest remaining value toward the end in each pass."],
                time_complexity="O(n^2)",
                space_complexity="O(1)",
            ),
            q(
                title="Selection Sort Numbers",
                companies=["Wipro", "HCL", "Cognizant", "Startup"],
                frequency="Medium",
                problem="Sort the list in ascending order using selection sort.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print the sorted list separated by spaces.",
                constraints="0 <= n <= 1000",
                sample_input="5\n29 10 14 37 13",
                sample_output="10 13 14 29 37",
                explanation="Each pass selects the smallest remaining value and places it at the current index.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
for i in range(n):
    min_index = i
    for j in range(i + 1, n):
        if numbers[j] < numbers[min_index]:
            min_index = j
    numbers[i], numbers[min_index] = numbers[min_index], numbers[i]
print(*numbers)
""",
                hints=["Find the minimum value in the unsorted part.", "Swap it into the current position."],
                time_complexity="O(n^2)",
                space_complexity="O(1)",
            ),
            q(
                title="Sort Words by Length",
                companies=["Zoho", "Freshworks", "Deloitte", "Startup"],
                frequency="Medium",
                problem="Sort words by increasing length. If two words have the same length, keep their original order.",
                input_format="One sentence.",
                output_format="Print the sorted words separated by spaces.",
                constraints="1 <= number of words <= 10000",
                sample_input="python is fun for interviews",
                sample_output="is fun for python interviews",
                explanation="Words are ordered by length while equal-length words keep their input order.",
                starter_code="""
sentence = input()

# Write your solution below
""",
                reference_solution="""
sentence = input()
words = sentence.split()
words.sort(key=len)
print(*words)
""",
                hints=["Use a stable sort.", "The key should be the word length."],
                time_complexity="O(n log n)",
                space_complexity="O(n)",
            ),
            q(
                title="Sort List Descending Without Built-in Sort",
                companies=["Amazon", "Microsoft", "Oracle", "Startup"],
                frequency="Medium",
                problem="Sort the numbers in descending order without using sort() or sorted().",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print numbers in descending order.",
                constraints="0 <= n <= 1000",
                sample_input="5\n3 1 9 2 7",
                sample_output="9 7 3 2 1",
                explanation="The largest values are placed first.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
for i in range(n):
    for j in range(0, n - i - 1):
        if numbers[j] < numbers[j + 1]:
            numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
print(*numbers)
""",
                hints=["A bubble-sort style comparison works.", "Swap when the left value is smaller than the right value."],
                time_complexity="O(n^2)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Patterns",
        "questions": [
            q(
                title="Right Triangle Stars",
                companies=["TCS", "Infosys", "Wipro", "Startup"],
                frequency="High",
                problem="Print a right triangle pattern of stars with n rows.",
                input_format="One integer n.",
                output_format="Print n lines of stars.",
                constraints="1 <= n <= 50",
                sample_input="4",
                sample_output="*\n**\n***\n****",
                explanation="Row i contains i stars.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(1, n + 1):
    print("*" * i)
""",
                hints=["Use a loop for rows.", "Repeat the star character i times."],
                time_complexity="O(n^2)",
                space_complexity="O(1)",
            ),
            q(
                title="Number Triangle",
                companies=["Accenture", "Cognizant", "Capgemini", "Startup"],
                frequency="High",
                problem="Print a triangle where row i contains the numbers from 1 to i.",
                input_format="One integer n.",
                output_format="Print n rows of increasing numbers.",
                constraints="1 <= n <= 50",
                sample_input="4",
                sample_output="1\n1 2\n1 2 3\n1 2 3 4",
                explanation="Each row starts at 1 and ends at the row number.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(1, n + 1):
    row = []
    for value in range(1, i + 1):
        row.append(str(value))
    print(" ".join(row))
""",
                hints=["Use a nested loop.", "Convert numbers to strings before joining."],
                time_complexity="O(n^2)",
                space_complexity="O(n)",
            ),
            q(
                title="Inverted Star Triangle",
                companies=["HCL", "Tech Mahindra", "Infosys", "Startup"],
                frequency="Medium",
                problem="Print an inverted right triangle of stars with n rows.",
                input_format="One integer n.",
                output_format="Print n lines, starting with n stars and ending with one star.",
                constraints="1 <= n <= 50",
                sample_input="4",
                sample_output="****\n***\n**\n*",
                explanation="The star count decreases by one on each row.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(n, 0, -1):
    print("*" * i)
""",
                hints=["Loop downward from n to 1.", "Repeat the star by the current row size."],
                time_complexity="O(n^2)",
                space_complexity="O(1)",
            ),
            q(
                title="Pyramid Star Pattern",
                companies=["Zoho", "Freshworks", "TCS", "Startup"],
                frequency="Medium",
                problem="Print a centered pyramid pattern with n rows.",
                input_format="One integer n.",
                output_format="Print n rows using spaces and stars.",
                constraints="1 <= n <= 50",
                sample_input="3",
                sample_output="  *\n ***\n*****",
                explanation="Each row has leading spaces and an odd number of stars.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(1, n + 1):
    spaces = " " * (n - i)
    stars = "*" * (2 * i - 1)
    print(spaces + stars)
""",
                hints=["Leading spaces decrease each row.", "Star count follows 2*i - 1."],
                time_complexity="O(n^2)",
                space_complexity="O(n)",
            ),
            q(
                title="Hollow Square Pattern",
                companies=["Deloitte", "Accenture", "Wipro", "Startup"],
                frequency="Medium",
                problem="Print a hollow square of side n using stars on the border.",
                input_format="One integer n.",
                output_format="Print n lines forming a hollow square.",
                constraints="1 <= n <= 50",
                sample_input="4",
                sample_output="****\n*  *\n*  *\n****",
                explanation="The border uses stars and the inside uses spaces.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
for i in range(n):
    if i == 0 or i == n - 1:
        print("*" * n)
    else:
        print("*" + " " * (n - 2) + "*")
""",
                hints=["First and last rows are full stars.", "Middle rows have stars only at both ends."],
                time_complexity="O(n^2)",
                space_complexity="O(n)",
            ),
        ],
    },
    {
        "topic_name": "Mathematics",
        "questions": [
            q(
                title="Prime Number Check",
                companies=["Amazon", "Google", "TCS", "Startup"],
                frequency="Very High",
                problem="Check whether the given number is prime.",
                input_format="One integer n.",
                output_format="Print YES if n is prime, otherwise print NO.",
                constraints="1 <= n <= 1000000",
                sample_input="29",
                sample_output="YES",
                explanation="29 has no positive divisors other than 1 and 29.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
if n < 2:
    print("NO")
else:
    is_prime = True
    value = 2
    while value * value <= n:
        if n % value == 0:
            is_prime = False
            break
        value += 1
    print("YES" if is_prime else "NO")
""",
                hints=["Numbers less than 2 are not prime.", "Check divisors only up to the square root."],
                time_complexity="O(sqrt(n))",
                space_complexity="O(1)",
            ),
            q(
                title="Armstrong Number Check",
                companies=["Infosys", "Zoho", "Freshworks", "Startup"],
                frequency="High",
                problem="Check whether a number equals the sum of its digits raised to the power of the digit count.",
                input_format="One non-negative integer n.",
                output_format="Print YES if it is an Armstrong number, otherwise print NO.",
                constraints="0 <= n <= 10^9",
                sample_input="153",
                sample_output="YES",
                explanation="153 has 3 digits and 1^3 + 5^3 + 3^3 = 153.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
digits = str(n)
power = len(digits)
total = 0
for ch in digits:
    total += int(ch) ** power
print("YES" if total == n else "NO")
""",
                hints=["Convert the number to a string to count digits.", "Raise each digit to that count."],
                time_complexity="O(d)",
                space_complexity="O(d)",
            ),
            q(
                title="Perfect Number Check",
                companies=["TCS", "Wipro", "Capgemini", "Startup"],
                frequency="Medium",
                problem="Check whether a number equals the sum of its proper divisors.",
                input_format="One positive integer n.",
                output_format="Print YES if it is perfect, otherwise print NO.",
                constraints="1 <= n <= 100000",
                sample_input="28",
                sample_output="YES",
                explanation="The proper divisors of 28 are 1, 2, 4, 7, and 14; their sum is 28.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
total = 0
for value in range(1, n):
    if n % value == 0:
        total += value
print("YES" if total == n else "NO")
""",
                hints=["Proper divisors exclude the number itself.", "Add every divisor smaller than n."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Leap Year Check",
                companies=["Deloitte", "Accenture", "Cognizant", "Startup"],
                frequency="High",
                problem="Determine whether a given year is a leap year.",
                input_format="One integer year.",
                output_format="Print YES for leap year, otherwise print NO.",
                constraints="1 <= year <= 9999",
                sample_input="2024",
                sample_output="YES",
                explanation="2024 is divisible by 4 and not by 100, so it is a leap year.",
                starter_code="""
year = int(input())

# Write your solution below
""",
                reference_solution="""
year = int(input())
is_leap = (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)
print("YES" if is_leap else "NO")
""",
                hints=["Years divisible by 400 are leap years.", "Years divisible by 100 but not 400 are not leap years."],
                time_complexity="O(1)",
                space_complexity="O(1)",
            ),
            q(
                title="Strong Number Check",
                companies=["Zoho", "Freshworks", "Infosys", "Startup"],
                frequency="Medium",
                problem="Check whether a number equals the sum of the factorials of its digits.",
                input_format="One non-negative integer n.",
                output_format="Print YES if it is a strong number, otherwise print NO.",
                constraints="0 <= n <= 100000",
                sample_input="145",
                sample_output="YES",
                explanation="1! + 4! + 5! = 1 + 24 + 120 = 145.",
                starter_code="""
n = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
factorials = [1] * 10
for value in range(1, 10):
    factorials[value] = factorials[value - 1] * value
total = 0
for ch in str(n):
    total += factorials[int(ch)]
print("YES" if total == n else "NO")
""",
                hints=["Precompute factorials for digits 0 through 9.", "Add the factorial of each digit."],
                time_complexity="O(d)",
                space_complexity="O(1)",
            ),
        ],
    },
    {
        "topic_name": "Mini Interview Challenges",
        "questions": [
            q(
                title="Compress Consecutive Characters",
                companies=["Amazon", "Microsoft", "Adobe", "Startup"],
                frequency="High",
                problem="Compress consecutive repeated characters by writing the character followed by its count.",
                input_format="One non-empty string text.",
                output_format="Print the compressed string.",
                constraints="1 <= length of text <= 100000",
                sample_input="aaabbc",
                sample_output="a3b2c1",
                explanation="There are three a characters, two b characters, and one c character consecutively.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
result = []
count = 1
for i in range(1, len(text)):
    if text[i] == text[i - 1]:
        count += 1
    else:
        result.append(text[i - 1] + str(count))
        count = 1
result.append(text[-1] + str(count))
print("".join(result))
""",
                hints=["Track the current run length.", "Flush a run when the character changes."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Validate Simple Password",
                companies=["Paytm", "Razorpay", "PhonePe", "Startup"],
                frequency="Medium",
                problem="A password is valid if it has at least 8 characters, one uppercase letter, one lowercase letter, and one digit.",
                input_format="One string password.",
                output_format="Print VALID or INVALID.",
                constraints="0 <= length of password <= 100000",
                sample_input="Bridge2026",
                sample_output="VALID",
                explanation="The password has enough length, uppercase letters, lowercase letters, and digits.",
                starter_code="""
password = input()

# Write your solution below
""",
                reference_solution="""
password = input()
has_upper = False
has_lower = False
has_digit = False
for ch in password:
    if ch.isupper():
        has_upper = True
    elif ch.islower():
        has_lower = True
    elif ch.isdigit():
        has_digit = True
valid = len(password) >= 8 and has_upper and has_lower and has_digit
print("VALID" if valid else "INVALID")
""",
                hints=["Use string methods like isupper and isdigit.", "Track each requirement with a boolean flag."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Find Pair with Given Sum",
                companies=["Google", "Amazon", "Microsoft", "Flipkart"],
                frequency="Very High",
                problem="Check whether any two different elements in the list add up to the target sum.",
                input_format="First line contains n. Second line contains n integers. Third line contains target.",
                output_format="Print YES if such a pair exists, otherwise print NO.",
                constraints="0 <= n <= 100000",
                sample_input="5\n2 7 11 15 1\n9",
                sample_output="YES",
                explanation="2 and 7 add up to 9.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
target = int(input())
seen = set()
found = False
for value in numbers:
    if target - value in seen:
        found = True
        break
    seen.add(value)
print("YES" if found else "NO")
""",
                hints=["For each value, look for target - value.", "Store previous values in a set."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
            q(
                title="Balanced Parentheses Basic",
                companies=["Amazon", "Adobe", "Oracle", "Startup"],
                frequency="High",
                problem="Check whether a string containing only parentheses has balanced opening and closing brackets.",
                input_format="One string containing only ( and ).",
                output_format="Print YES if balanced, otherwise print NO.",
                constraints="0 <= length of string <= 100000",
                sample_input="(()())",
                sample_output="YES",
                explanation="Every closing parenthesis has a matching earlier opening parenthesis.",
                starter_code="""
text = input()

# Write your solution below
""",
                reference_solution="""
text = input()
balance = 0
valid = True
for ch in text:
    if ch == "(":
        balance += 1
    else:
        balance -= 1
    if balance < 0:
        valid = False
        break
print("YES" if valid and balance == 0 else "NO")
""",
                hints=["Increase balance for '(' and decrease for ')'.", "Balance should never become negative and should end at zero."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Expand Run Length Encoding",
                companies=["Zoho", "Freshworks", "Meesho", "Startup"],
                frequency="Medium",
                problem="Expand a simple encoded string where every letter is followed by a single digit count.",
                input_format="One encoded string such as a3b2.",
                output_format="Print the expanded string.",
                constraints="Encoded string length is even and at most 100000; counts are from 0 to 9.",
                sample_input="a3b2c1",
                sample_output="aaabbc",
                explanation="a3 expands to aaa, b2 expands to bb, and c1 expands to c.",
                starter_code="""
encoded = input()

# Write your solution below
""",
                reference_solution="""
encoded = input()
result = []
for i in range(0, len(encoded), 2):
    ch = encoded[i]
    count = int(encoded[i + 1])
    result.append(ch * count)
print("".join(result))
""",
                hints=["Read characters in pairs.", "The second character in each pair is the repetition count."],
                time_complexity="O(n + output_length)",
                space_complexity="O(output_length)",
            ),
            q(
                title="Maximum Consecutive Ones",
                companies=["Flipkart", "PhonePe", "Razorpay", "Startup"],
                frequency="High",
                problem="Find the longest continuous run of 1 values in a binary list.",
                input_format="First line contains n. Second line contains n values, each 0 or 1.",
                output_format="Print the maximum consecutive ones count.",
                constraints="0 <= n <= 100000",
                sample_input="8\n1 1 0 1 1 1 0 1",
                sample_output="3",
                explanation="The longest block of 1 values has length 3.",
                starter_code="""
n = int(input())
bits = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
bits = list(map(int, input().split())) if n else []
best = 0
current = 0
for bit in bits:
    if bit == 1:
        current += 1
        best = max(best, current)
    else:
        current = 0
print(best)
""",
                hints=["Reset the current streak when you see 0.", "Keep a best streak separately."],
                time_complexity="O(n)",
                space_complexity="O(1)",
            ),
            q(
                title="Leader Elements in List",
                companies=["Amazon", "Microsoft", "Paytm", "Startup"],
                frequency="Medium",
                problem="An element is a leader if no element to its right is greater than it. Print all leaders in original order.",
                input_format="First line contains n. Second line contains n integers.",
                output_format="Print leader values separated by spaces.",
                constraints="0 <= n <= 100000",
                sample_input="6\n16 17 4 3 5 2",
                sample_output="17 5 2",
                explanation="17 has no greater value to its right, 5 is greater than values after it, and 2 is the last element.",
                starter_code="""
n = int(input())
numbers = list(map(int, input().split())) if n else []

# Write your solution below
""",
                reference_solution="""
n = int(input())
numbers = list(map(int, input().split())) if n else []
leaders = []
max_right = None
for value in reversed(numbers):
    if max_right is None or value >= max_right:
        leaders.append(value)
        max_right = value
leaders.reverse()
print(*leaders)
""",
                hints=["Scan from right to left.", "Track the maximum value seen on the right."],
                time_complexity="O(n)",
                space_complexity="O(n)",
            ),
        ],
    },
]


def _description(topic_name: str, question: dict[str, Any]) -> str:
    sections = [
        ("Topic", topic_name),
        ("Companies Asked", ", ".join(question["companies"])),
        ("Estimated Interview Frequency", question["frequency"]),
        ("Problem Statement", question["problem"]),
        ("Input Format", question["input_format"]),
        ("Output Format", question["output_format"]),
        ("Constraints", question["constraints"]),
        ("Sample Input", question["sample_input"]),
        ("Sample Output", question["sample_output"]),
        ("Explanation", question["explanation"]),
        ("Expected Time Complexity", question["time_complexity"]),
        ("Expected Space Complexity", question["space_complexity"]),
    ]
    return "\n\n".join(f"{label}:\n{value}" for label, value in sections)


def _hidden_metadata(topic_name: str, question: dict[str, Any]) -> str:
    return json.dumps(
        {
            "kind": "practice_lab_interview_question",
            "topic": topic_name,
            "companies": question["companies"],
            "estimated_interview_frequency": question["frequency"],
            "expected_output": question["sample_output"],
            "reference_solution": question["reference_solution"],
            "hints": question["hints"],
            "expected_time_complexity": question["time_complexity"],
            "expected_space_complexity": question["space_complexity"],
        },
        ensure_ascii=True,
        indent=2,
    )


def build_practice_lab_topics() -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    question_count = 0

    for topic in INTERVIEW_LIBRARY:
        topic_name = topic["topic_name"]
        questions = []
        for question in topic["questions"]:
            title_key = question["title"].strip().lower()
            if title_key in seen_titles:
                raise ValueError(f"Duplicate Practice Lab question title: {question['title']}")
            seen_titles.add(title_key)
            questions.append(
                {
                    "title": question["title"],
                    "description": _description(topic_name, question),
                    "difficulty": "Easy",
                    "starter_code": question["starter_code"],
                    "expected_output": _hidden_metadata(topic_name, question),
                }
            )
            question_count += 1
        topics.append({"topic_name": topic_name, "questions": questions})

    if question_count != 75:
        raise ValueError(f"Practice Lab interview library must contain 75 questions, found {question_count}")

    return topics
