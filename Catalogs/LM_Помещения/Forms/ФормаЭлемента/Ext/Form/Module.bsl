﻿

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	
	Если ЗначениеЗаполнено(Объект.Цвет) Тогда
		Попытка
			Элементы.ПриНажатииКнопкиВыборЦвета.ЦветФона = WebЦвета[Объект.Цвет];
			Элементы.ПриНажатииКнопкиВыборЦвета.Заголовок = WebЦвета[Объект.Цвет];
		Исключение
		КонецПопытки;
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура ПриНажатииКнопкиВыборЦвета(Команда)
	
	Кнопка = ЭтаФорма.ТекущийЭлемент;
	
	Обработчик = Новый ОписаниеОповещения("ПриВыбореWebЦвета", ЭтаФорма);
	Режим = РежимОткрытияОкнаФормы.БлокироватьОкноВладельца;
	ДопПарам = Новый Структура("ИмяКнопки", Кнопка.Имя);
	
	//Форма текущей демо обработки
	ОткрытьФорму("Обработка.LM_ВыборWebЦвета.Форма.ПалитраWebЦветовУправляемая", ДопПарам,,,,, Обработчик, Режим);
	
КонецПроцедуры

&НаКлиенте
Процедура ПриВыбореWebЦвета(ВыбраныйWebЦвет, ДополнительныеПараметры) Экспорт
	
	//Обработка выбора цветв
	Если НЕ ВыбраныйWebЦвет = Неопределено Тогда
		ИмяКнопки = ЭтаФорма.ТекущийЭлемент.Имя;
		Элементы[ИмяКнопки].ЦветФона  = ВыбраныйWebЦвет;
		Элементы[ИмяКнопки].Заголовок = ВыбраныйWebЦвет;
		Попытка
			ВыбЦвет = Сред(ВыбраныйWebЦвет,0,Найти(ВыбраныйWebЦвет,"(")-2);
			ВыбЦвет = СтрЗаменить(ВыбЦвет,"-","");
			ВыбЦвет = СтрЗаменить(ВыбЦвет," ","");
			Объект.Цвет = ВыбЦвет;
		Исключение
			Объект.Цвет = ВыбраныйWebЦвет; 
		КонецПопытки;
	КонецЕсли; 
	
КонецПроцедуры

