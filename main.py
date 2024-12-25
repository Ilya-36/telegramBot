import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters,
)
from datetime import datetime

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

(
    PLAN_MEETING_DATE,
    PLAN_MEETING_TIME,
    PLAN_MEETING_PARTICIPANTS,
    ADD_TASK_DESCRIPTION,
    ADD_TASK_DUE_DATE,
    ADD_TASK_ASSIGNEE,
    MARK_TASK_COMPLETE,
) = range(7)

meetings = {}
tasks = {}


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот, который поможет вам с планированием встреч и задач."
        "Используйте /plan_meeting, чтобы запланировать встречу, /add_task, чтобы добавить новую задачу,"
        "/complete_task, чтобы отметить задачу как выполненную, и /list_tasks, чтобы увидеть задачи."
        "Используйте /help, чтобы увидеть все доступные команды."
    )


async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Команда помощи\n"
        "/plan_meeting - Запланировать встречу\n"
        "/add_task - Добавить задачу\n"
        "/list_tasks - Вывести список всех задач\n"
        "/complete_task - Отметить задачу как выполненную\n"
        "/cancel - Отменить текущую операцию\n"
    )


async def plan_meeting(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Введите дату встречи (ГГГГ-ММ-ДД):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PLAN_MEETING_DATE


async def plan_meeting_date(update: Update, context: CallbackContext) -> int:
    date_str = update.message.text
    logging.info(f"plan_meeting_date: Received date_str='{date_str}'")
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        context.user_data["meeting_date"] = date
        await update.message.reply_text(
            "Введите временной диапазон встречи (ЧЧ:ММ-ЧЧ:ММ):"
        )
        logging.info(f"plan_meeting_date: Returning PLAN_MEETING_TIME")
        return PLAN_MEETING_TIME
    except ValueError as e:
        await update.message.reply_text(
            "Неверный формат даты. Используйте ГГГГ-ММ-ДД. Попробуйте еще раз."
        )
        logging.info(f"plan_meeting_date: ValueError occurred: {e}. Returning PLAN_MEETING_DATE")
        return PLAN_MEETING_DATE


async def plan_meeting_time(update: Update, context: CallbackContext) -> int:
    time_range = update.message.text
    logging.info(f"plan_meeting_time: Received time_range='{time_range}'")
    try:
        datetime.strptime(time_range.split('-')[0], "%H:%M")
        datetime.strptime(time_range.split('-')[1], "%H:%M")
        context.user_data["meeting_time"] = time_range
        await update.message.reply_text(
            "Введите участников (идентификаторы, разделенные запятыми):"
        )
        logging.info(f"plan_meeting_time: Returning PLAN_MEETING_PARTICIPANTS")
        return PLAN_MEETING_PARTICIPANTS
    except ValueError as e:
        await update.message.reply_text(
            "Неверный формат времени. Используйте ЧЧ:ММ-ЧЧ:ММ. Попробуйте еще раз."
        )
        logging.info(f"plan_meeting_time: ValueError occurred: {e}. Returning PLAN_MEETING_TIME")
        return PLAN_MEETING_TIME


async def plan_meeting_participants(update: Update, context: CallbackContext) -> int:
    participants = [p.strip() for p in update.message.text.split(",")]
    context.user_data["meeting_participants"] = participants
    meeting_date = context.user_data["meeting_date"]
    meeting_time = context.user_data["meeting_time"]
    meeting_participants = context.user_data["meeting_participants"]
    meeting_id = len(meetings) + 1
    meetings[meeting_id] = {
        "date": meeting_date,
        "time": meeting_time,
        "participants": meeting_participants,
    }
    await update.message.reply_text(
        f"Встреча запланирована на {meeting_date} в {meeting_time} с {', '.join(meeting_participants)}."
        f" Идентификатор встречи: {meeting_id}. Вы можете ссылаться на эту встречу, используя идентификатор."
    )
    logging.info(f"plan_meeting_participants: Returning ConversationHandler.END")
    return ConversationHandler.END


async def add_task(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Введите описание задачи:")
    logging.info(f"add_task: Returning ADD_TASK_DESCRIPTION")
    return ADD_TASK_DESCRIPTION


async def add_task_description(update: Update, context: CallbackContext) -> int:
    task_description = update.message.text
    logging.info(f"add_task_description: Received task_description='{task_description}'")
    context.user_data["task_description"] = task_description
    await update.message.reply_text("Введите дату платежа (ГГГГ-ММ-ДД):")
    logging.info(f"add_task_description: Returning ADD_TASK_DUE_DATE")
    return ADD_TASK_DUE_DATE


async def add_task_due_date(update: Update, context: CallbackContext) -> int:
    due_date_str = update.message.text
    logging.info(f"add_task_due_date: Received due_date_str='{due_date_str}'")
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        context.user_data["task_due_date"] = due_date
        await update.message.reply_text("Введите имя ответственного (необязательно):")
        logging.info(f"add_task_due_date: Returning ADD_TASK_ASSIGNEE")
        return ADD_TASK_ASSIGNEE
    except ValueError as e:
        await update.message.reply_text(
            "Неверный формат даты. Используйте ГГГГ-ММ-ДД. Попробуйте еще раз."
        )
        logging.info(f"add_task_due_date: ValueError occurred: {e}. Returning ADD_TASK_DUE_DATE")
        return ADD_TASK_DUE_DATE


async def add_task_assignee(update: Update, context: CallbackContext) -> int:
    assignee = update.message.text.strip()
    logging.info(f"add_task_assignee: Received assignee='{assignee}'")
    task_description = context.user_data["task_description"]
    due_date = context.user_data["task_due_date"]
    task_id = len(tasks) + 1
    tasks[task_id] = {
        "description": task_description,
        "due_date": due_date,
        "assignee": assignee,
        "completed": False,
    }
    await update.message.reply_text(
        f"Добавлено задание: {task_description} срок сдачи {due_date}. Идентификатор задачи: {task_id}. Назначено: {assignee}. "
        "Вы можете обратиться к этой задаче, используя идентификатор."
    )
    logging.info(f"add_task_assignee: Returning ConversationHandler.END")
    return ConversationHandler.END


async def list_tasks(update: Update, context: CallbackContext) -> None:
    if not tasks:
        await update.message.reply_text("Задачи не найдены.")
        return

    message = "Текущие задачи:\n"
    for task_id, task_data in tasks.items():
        description = task_data["description"]
        due_date = task_data["due_date"]
        assignee = task_data["assignee"]
        completed = task_data["completed"]
        status = "[DONE]" if completed else "[PENDING]"
        message += f"ID: {task_id} {status}, Описание: {description}, Срок: {due_date}, Уполномоченный: {assignee}\n"

    await update.message.reply_text(message)
    logging.info("list_tasks: Tasks listed.")

async def complete_task(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Введите идентификатор задачи, которую вы хотите отметить как выполненную:"
    )
    logging.info(f"complete_task: Returning MARK_TASK_COMPLETE")
    return MARK_TASK_COMPLETE

async def mark_task_complete(update: Update, context: CallbackContext) -> int:
    task_id_str = update.message.text.strip()
    logging.info(f"mark_task_complete: Received task_id_str='{task_id_str}'")
    try:
      task_id = int(task_id_str)
      if task_id in tasks:
          tasks[task_id]['completed'] = True
          await update.message.reply_text(f"Задача {task_id} помечена как завершенная.")
          logging.info(f"mark_task_complete: Task {task_id} marked as complete. Returning ConversationHandler.END")
      else:
        await update.message.reply_text("Неверный идентификатор задачи. Попробуйте еще раз.")
        logging.info(f"mark_task_complete: Invalid task ID. Returning MARK_TASK_COMPLETE")
        return MARK_TASK_COMPLETE
    except ValueError as e:
         await update.message.reply_text("Неверный идентификатор задачи. Укажите номер. Попробуйте еще раз.")
         logging.info(f"mark_task_complete: ValueError occurred: {e}. Returning MARK_TASK_COMPLETE")
         return MARK_TASK_COMPLETE
    logging.info(f"mark_task_complete: Returning ConversationHandler.END")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена.")
    logging.info(f"cancel: Operation cancelled. Returning ConversationHandler.END")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token("Введите токен бота").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("plan_meeting", plan_meeting)],
        states={
            PLAN_MEETING_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, plan_meeting_date)
            ],
            PLAN_MEETING_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, plan_meeting_time)
            ],
            PLAN_MEETING_PARTICIPANTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, plan_meeting_participants)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    conv_handler_task = ConversationHandler(
        entry_points=[CommandHandler("add_task", add_task)],
        states={
            ADD_TASK_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_description)
            ],
            ADD_TASK_DUE_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_due_date)
            ],
            ADD_TASK_ASSIGNEE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_assignee)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler_task)

    conv_handler_complete_task = ConversationHandler(
       entry_points=[CommandHandler("complete_task", complete_task)],
       states={
          MARK_TASK_COMPLETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mark_task_complete)]
       },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler_complete_task)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list_tasks", list_tasks))

    application.run_polling()


if __name__ == "__main__":
    main()
