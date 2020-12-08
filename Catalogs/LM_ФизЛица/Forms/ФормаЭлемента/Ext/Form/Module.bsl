﻿&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	
	Если Объект.Ссылка.Пустая() Тогда
		Попытка
			Объект.Родитель = Справочники.LM_ФизЛица[Параметры.Ключ2.Группа];
		Исключение
		КонецПопытки;
	КонецЕсли;
		
КонецПроцедуры

#Region Работа_с_фото

Процедура ПоказатьКартинки()
	
	Если НЕ Объект.Фото.Пустая() Тогда
		Фото = ПоместитьВоВременноеХранилище(Объект.Фото.Файл.Получить());
	Иначе
		Фото = "";
	КонецЕсли;
	
КонецПроцедуры
&НаКлиенте
Процедура ВыбратьФото(Команда)	
	Оповещение = Новый ОписаниеОповещения("ОбработатьВыборФайла",ЭтотОбъект);
	НачатьПомещениеФайла(Оповещение,,,Истина,УникальныйИдентификатор);	
КонецПроцедуры
&НаКлиенте
Процедура ОбработатьВыборФайла(Результат, Адрес, ВыбранноеИмяФайла, ДополнительныеПараметры) Экспорт
	
	Если Не Результат Тогда
		Возврат;
	КонецЕсли;
	
	Фото = Адрес;
	
	ЗаписатьНовуюКартинкуНаСервере();	
	
КонецПроцедуры
Процедура ЗаписатьНовуюКартинкуНаСервере()
	
	Если Объект.Фото.Пустая() Тогда
		НовыйФайлКартинки = Справочники.LM_Фото.СоздатьЭлемент();
	Иначе
		НовыйФайлКартинки = Объект.Фото.ПолучитьОбъект();
	КонецЕсли; 
	
	НовыйФайлКартинки.Файл = Новый ХранилищеЗначения(ПолучитьИзВременногоХранилища(Фото));
	НовыйФайлКартинки.Наименование = Объект.Наименование;
	
	Попытка
		НовыйФайлКартинки.Записать();
		Если Объект.Фото.Пустая() Тогда
			Объект.Фото = НовыйФайлКартинки.Ссылка;
		КонецЕсли;
	Исключение
		Сообщить("Не удалось сохранить фотографию! " +ОписаниеОшибки());
	КонецПопытки;
	
КонецПроцедуры 	
&НаКлиенте
Процедура ФотоОбъектОчистка(Элемент, СтандартнаяОбработка)
	Фото = Неопределено; 
КонецПроцедуры
&НаКлиенте
Процедура ФотоПриИзменении(Элемент) 	
	ПоказатьКартинки();
КонецПроцедуры

#EndRegion


//Расчет возраста
&НаКлиенте 
Процедура ДатаРожденияПриИзменении(Элемент)
	
	РассчитатьВозраст();
	
КонецПроцедуры

&НаСервере
Процедура РассчитатьВозраст()
	
	Если ЗначениеЗаполнено(Объект.ДатаРождения) Тогда
		//Объект.Возраст = Цел((ТекущаяДата()- Объект.ДатаРождения)/60/60/24/365); //Годы
		
		Объект.Возраст = Год(ТекущаяДата()) - Год(Объект.ДатаРождения) 
                    - ?(Месяц(ТекущаяДата()) < Месяц(Объект.ДатаРождения) 
                        Или Месяц(ТекущаяДата()) = Месяц(Объект.ДатаРождения) И День(ТекущаяДата()) < День(Объект.ДатаРождения), 
                         1, 0);
	Иначе                          
		Объект.Возраст = Неопределено;
	КонецЕсли;
	
КонецПроцедуры
//Конец расчет возраста


&НаКлиенте
Процедура ПриЗакрытии(ЗавершениеРаботы)
	
	Если ЗначениеЗаполнено(Объект.Ссылка) Тогда
		Оповестить(Объект.Ссылка);
	КонецЕсли;

КонецПроцедуры 

&НаКлиенте
Процедура ДекорацияСсылкаHttpНажатие(Элемент)
	
	Если ЗначениеЗаполнено(Объект.Http) Тогда
		ПерейтиПоНавигационнойСсылке(Объект.Http);
	КонецЕсли;

КонецПроцедуры

&НаКлиенте
Процедура РодительСоздание(Элемент, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	ПараметрыСтроки = Новый Структура;
	
	Назв = СокрЛП(Элемент.ТекстРедактирования);
	
	Если Найти(Назв," ") > 0 Тогда
		Симв1 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Наименование",Лев(Назв,Симв1-1));
		Назв = СокрЛП(Сред(Назв,Симв1+1));
	Иначе
		ПараметрыСтроки.Вставить("Наименование",Назв);
		Назв = "";
	КонецЕсли;
	
	ПараметрыСтроки.Вставить("Группа","Родители");
	
	Пар = Новый Структура("Ключ2", ПараметрыСтроки);
	
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаЭлемента",Пар,ЭтотОбъект,ЭтаФорма.УникальныйИдентификатор,ВариантОткрытияОкна.ОтдельноеОкно,,,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);

КонецПроцедуры

&НаКлиенте
Процедура ОткрытьВзаиморасчеты(Команда)
	
	СтандартнаяОбработка = Ложь;
	ОткрытьВзаиморасчетыНаКлиенте();
	
КонецПроцедуры
Функция ОткрытьВзаиморасчетыНаСервере()
	
	КомпоновщикНастроек = Отчеты.LM_Взаиморасчеты.Создать().КомпоновщикНастроек; 
	Настройки 			= КомпоновщикНастроек.Настройки; 
	
	ЭлементНастройки = Настройки.ПараметрыДанных.НайтиЗначениеПараметра(Новый ПараметрКомпоновкиДанных("Период")); 
	//ЭлементНастройки.Значение.ДатаНачала    = '00010101';//НачалоГода(ТекущаяДата());
	//ЭлементНастройки.Значение.ДатаОкончания = '00010101';//КонецГода(ТекущаяДата());
	Если ЗначениеЗаполнено(ЭлементНастройки.ИдентификаторПользовательскойНастройки) Тогда 
		ПользовательскийПараметр = КомпоновщикНастроек.ПользовательскиеНастройки.Элементы.Найти(ЭлементНастройки.ИдентификаторПользовательскойНастройки); 
		Если ТипЗнч(ПользовательскийПараметр) = Тип("ЗначениеПараметраНастроекКомпоновкиДанных") Тогда 
			//ПользовательскийПараметр.Значение = ЭлементНастройки.Значение;
			ПользовательскийПараметр.Использование = Ложь;
		КонецЕсли; 
	КонецЕсли; 
	
	Если Объект.ЭтоПедагог Тогда
		ОтборФизЛицо = Новый ПолеКомпоновкиДанных("Педагог");
	Иначе   		
		ОтборФизЛицо = Новый ПолеКомпоновкиДанных("Клиент");
		//ОтборПериод = Новый ПолеКомпоновкиДанных("Период");
	КонецЕсли;

	
	Для Каждого ЭлементНастройки Из Настройки.Отбор.Элементы Цикл 
		Если ЭлементНастройки.ЛевоеЗначение = ОтборФизЛицо Тогда 
			ЭлементНастройки.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно; 
			ЭлементНастройки.ПравоеЗначение = Объект.Ссылка; 
			ЭлементНастройки.Использование = Истина; 
			Если ЗначениеЗаполнено(ЭлементНастройки.ИдентификаторПользовательскойНастройки) Тогда 
				ПользовательскийПараметр = КомпоновщикНастроек.ПользовательскиеНастройки.Элементы.Найти(ЭлементНастройки.ИдентификаторПользовательскойНастройки); 
				Если ТипЗнч(ПользовательскийПараметр) = Тип("ЭлементОтбораКомпоновкиДанных") Тогда 
					ПользовательскийПараметр.ВидСравнения = ЭлементНастройки.ВидСравнения; 
					ПользовательскийПараметр.ПравоеЗначение = ЭлементНастройки.ПравоеЗначение; 
					ПользовательскийПараметр.Использование = ЭлементНастройки.Использование; 
				КонецЕсли; 
			КонецЕсли;
			Прервать; 
		КонецЕсли; 
	КонецЦикла; 
	
	ПараметрыОткрытия = Новый Структура(); 
	ПараметрыОткрытия.Вставить("СформироватьПриОткрытии", Истина); 
	ПараметрыОткрытия.Вставить("Вариант", Настройки); 
	ПараметрыОткрытия.Вставить("ПользовательскиеНастройки", КомпоновщикНастроек.ПользовательскиеНастройки); 
	
	Возврат ПараметрыОткрытия;
	
КонецФункции
&НаКлиенте
Процедура ОткрытьВзаиморасчетыНаКлиенте()
	
	Если ЗначениеЗаполнено(Объект.Ссылка) Тогда		
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере();
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	Иначе
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", , ЭтаФорма);
	КонецЕсли;
	
КонецПроцедуры

/////Цвет
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
/////Цвет

&НаКлиенте
Процедура ПриОткрытии(Отказ)	
	ОбновитьВидимостьЭлементов(); 	
КонецПроцедуры

&НаКлиенте
Процедура ВозрастПриИзменении(Элемент)
	Объект.ДатаРождения = Неопределено;
КонецПроцедуры

&НаКлиенте
Процедура ГруппаСтраницыПриСменеСтраницы(Элемент, ТекущаяСтраница)
	
	Если Элементы.ГруппаСтраницы.ТекущаяСтраница = Элементы.ГруппаСтраница2 Тогда
		
		Если Объект.Ссылка.Пустая() Тогда
			Кл = Неопределено;
		Иначе
			Кл = Объект.Ссылка;	
		КонецЕсли;
		
		Если Объект.ЭтоПедагог Тогда
		Иначе
			Документы.Параметры.УстановитьЗначениеПараметра("Клиент", Кл);
		КонецЕсли;
		
	КонецЕсли; 
	
КонецПроцедуры

Процедура ЗаполнитьИтоги()
	
	Если Объект.Ссылка.Пустая() Тогда
		Возврат;
	КонецЕсли;
	
	
	Долги.Очистить();
	Элементы.ГруппаЗадолженность.Заголовок = "Задолженность по всем предметам";
		
	Запрос = Новый Запрос;
	
	Если Объект.ЭтоПедагог Тогда
		
	Иначе 		
		
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.СуммаКонечныйОстаток КАК Долг,
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.ПредметОбучения КАК Предмет
		|ИЗ
		|	РегистрНакопления.LM_СписанияСуммЗаУроки.ОстаткиИОбороты(, , Авто, , ) КАК LM_СписанияСуммЗаУрокиОстаткиИОбороты
		|ГДЕ
		|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.Клиент = &Клиент";
		Запрос.УстановитьПараметр("Клиент", Объект.Ссылка);
		ТЗДолги = Запрос.Выполнить().Выгрузить();
		
		Для Каждого стр из ТЗДолги Цикл
			НовСТр = Долги.Добавить();
			НовСТр.Предмет 	= стр.Предмет;
			НовСТр.Долг 	= стр.Долг;
		КонецЦикла;
		
		Если ТЗДолги.Количество()>0 Тогда
			ОстДенег = Долги.Итог("Долг");
			Элементы.ГруппаЗадолженность.Заголовок = "Задолженность итого по всем предметам: " +?(ОстДенег>0,Формат(ОстДенег,"ЧДЦ=2; ЧФ=+Ч"),Формат(ОстДенег,"ЧДЦ=2"));
		КонецЕсли;
		
		
		// Проверка по тарифу
		Если ЗначениеЗаполнено(Объект.Тариф) Тогда
			
			ОстатокДенегПоТарифу = "";
			ОстатокЕдиницПоТарифу = 0;
			
			Запрос = Новый Запрос;
			Запрос.Текст = 
			"ВЫБРАТЬ
			|	LM_СписанияСуммЗаУрокиОстаткиИОбороты.СуммаКонечныйОстаток КАК СуммаКонечныйОстаток
			|ИЗ
			|	РегистрНакопления.LM_СписанияСуммЗаУроки.ОстаткиИОбороты(
			|			,
			|			,
			|			,
			|			,
			|			Тариф = &Тариф
			|				И Клиент = &Ученик) КАК LM_СписанияСуммЗаУрокиОстаткиИОбороты";
			Запрос.УстановитьПараметр("Тариф", Объект.Тариф);
			Запрос.УстановитьПараметр("Ученик", Объект.Ссылка);
			ОстатокПоТарифу = Запрос.Выполнить().Выгрузить();
			
			Если ОстатокПоТарифу.Количество()>0 Тогда
				
				Если Объект.Тариф.Сумма <> 0 Тогда
					КолЕдиницПоТарифу = ?(Объект.Тариф.КоличествоУроков<>0,Объект.Тариф.КоличествоУроков,Объект.Тариф.КоличествоЧасов);
					ЦенаЗаЕдиницуТарифа = Объект.Тариф.Сумма / КолЕдиницПоТарифу;
					Если ОстатокПоТарифу[0].СуммаКонечныйОстаток > 0 Тогда
						ОстатокДенегПоТарифу = Формат(ОстатокПоТарифу[0].СуммаКонечныйОстаток,"ЧДЦ=2; ЧФ=+Ч");
						Элементы.ОстатокДенегПоТарифу1.ЦветТекста =  WebЦвета.ТемноЗеленый;
						ОстатокЕдиницПоТарифу = ОстатокПоТарифу[0].СуммаКонечныйОстаток / ЦенаЗаЕдиницуТарифа;
					ИначеЕсли ОстатокПоТарифу[0].СуммаКонечныйОстаток < 0 Тогда
						ОстатокДенегПоТарифу = ОстатокПоТарифу[0].СуммаКонечныйОстаток;
						Элементы.ОстатокДенегПоТарифу1.ЦветТекста =  WebЦвета.ТемноОранжевый;
					КонецЕсли;
				КонецЕсли;
				
			КонецЕсли;
						
		КонецЕсли;
	КонецЕсли;
		
КонецПроцедуры
&НаКлиенте
Процедура ОткрытьВзаиморасчетыНаКлиенте2(Элемент) 	
	ОткрытьВзаиморасчетыНаКлиенте();	
КонецПроцедуры 

&НаКлиенте
Процедура ЭтоПедагогПриИзменении(Элемент)	
	ОбновитьВидимостьЭлементов();	
КонецПроцедуры

&НаКлиенте
Процедура ОбновитьВидимостьЭлементов()

	Если ЗначениеЗаполнено(Объект.Цвет) Тогда
		Элементы.ПриНажатииКнопкиВыборЦвета.ЦветФона = WebЦвета[Объект.Цвет];
	КонецЕсли;
	
	ЗаполнитьИтоги();
	
	Если Объект.ЭтоПедагог Тогда		
		Элементы.Родитель.Видимость = Ложь;
		//Элементы.ГруппаГруппыОбучения.Видимость = Ложь;
		Элементы.СтавкаПедагога.Видимость = Истина;
		Элементы.Скидка.Видимость = Ложь;
		Элементы.Тариф.Видимость = Ложь;
	Иначе
		Элементы.Родитель.Видимость = Истина;
		//Элементы.ГруппаГруппыОбучения.Видимость = Истина;
		Элементы.СтавкаПедагога.Видимость = Ложь;
		Элементы.Скидка.Видимость = Истина;
		Элементы.Тариф.Видимость = Истина;
	КонецЕсли;
	
	ПоказатьКартинки();

КонецПроцедуры

&НаКлиенте
Процедура ДолгиВыбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)
	ОткрытьВзаиморасчетыНаКлиенте();
КонецПроцедуры


&НаКлиенте
Процедура ТарифПриИзменении(Элемент)
	ОбновитьВидимостьЭлементов();
КонецПроцедуры


&НаКлиенте
Процедура ОстатокДенегПоТарифуНажатие(Элемент, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	ОткрытьВзаиморасчетыНаКлиенте();
	
КонецПроцедуры

