from Task3.Weaviate.HybridSearch import search_precise_answer
from Task3.Weaviate.HybridSearch import extract_relevant_part

def interactive_search():
    print("Введите ваш запрос (или 'exit' для выхода):")

    while True:
        try:
            # Получаем запрос от пользователя
            user_input = input("\nЗАПРОС:\n> ").strip()

            if user_input.lower() in ['exit', 'выход', 'quit']:
                print("Завершение работы системы...")
                break

            if not user_input:
                print("Пожалуйста, введите непустой запрос")
                continue

            # Выполняем поиск
            result = search_precise_answer(user_input)

            # Форматируем вывод
            print("\nОТВЕТ:")
            if result["status"] == "success":
                # Вывод основного ответа
                print(result["answer"])

                # Поиск и вывод определений терминов
                terms = find_terms_in_text(result["answer"])
                if terms:
                    print("\nОпределения терминов:")
                    for term in terms:
                        print(f"\n{term['term']}:")
                        print(term['definition'])

                print(f"\n(Источник: {result['source']}, score: {result['score']:.3f})")
            else:
                print(result["message"])

        except KeyboardInterrupt:
            print("\nЗавершение работы по запросу пользователя")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {str(e)}")
            continue


if __name__ == "__main__":
    interactive_search()