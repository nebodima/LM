﻿
&НаСервере
Процедура ПересчитатьТабличнуюЧасть()
	
	Документы.LM_Урок.РассчитатьТабличнуюЧасть(Объект);
	
	Объект.Сумма 		= Объект.Ученики.Итог("Сумма");
	Объект.СуммаСкидки 	= Объект.Ученики.Итог("СуммаСкидки");
	
	Объект.Окончание = Объект.Дата - ('00010101'-Объект.КоличествоЧасов);
	
	ОпределитьЦветРеквизитов();
	
КонецПроцедуры

&НаСервере
Процедура ОбновитьВидимость()
	
	КоличествоНачисленийПедагогу = 0;
	КоличествоДисконтныхКарт = 0;
	
	Для Каждого Стр из Объект.Ученики Цикл
		Стр.ЗадолженностьПоПредмету = РассчитатьЗадолженность(Стр.Ученик, Объект.ПредметОбучения, Объект.Организация);
		Стр.ЗадолженностьОбщая		= РассчитатьЗадолженность(Стр.Ученик, Неопределено, Объект.Организация);
		Стр.ОстатокБонусов 			= РассчитатьОстатокБонусов(Стр.Ученик, Стр.ДисконтнаяКарта, Объект.Организация);
		
		Если ЗначениеЗаполнено(Стр.ДисконтнаяКарта) Тогда
			КоличествоДисконтныхКарт	= КоличествоДисконтныхКарт + 1;
		КонецЕсли;
	КонецЦикла;
	
	Для Каждого СтрПед из Объект.НачисленияПедагогу Цикл
		Если ЗначениеЗаполнено(СтрПед.СуммаНачисления) Тогда
			КоличествоНачисленийПедагогу = КоличествоНачисленийПедагогу + 1;
		КонецЕсли;
	КонецЦикла;
		
	Если КоличествоНачисленийПедагогу>0 Тогда
		Элементы.ГруппаНачисленияПедагогу.Заголовок = ""+КоличествоНачисленийПедагогу+ " начислений педагогу (" +Формат(Объект.НачисленияПедагогу.Итог("СуммаНачисления"),"ЧДЦ=2")+")";
	КонецЕсли;
	
	Если КоличествоДисконтныхКарт>0 Тогда
		Элементы.ГруппаДисконтныеКарты.Заголовок = ""+КоличествоДисконтныхКарт+ " Дисконтных карт (" +Формат(Объект.Ученики.Итог("СуммаБонусов"),"ЧДЦ=2")+")";
	КонецЕсли;
	
	Элементы.ГруппаУченикиСтраница.Заголовок = "Ученики (" +Объект.Ученики.Количество()+")";
	
	ОпределитьЦветРеквизитов();
	
КонецПроцедуры

Процедура ОпределитьЦветРеквизитов()
	
	Если ЗначениеЗаполнено(Объект.Помещение) и ЗначениеЗаполнено(Объект.Помещение.Цвет) Тогда
		Элементы.Помещение.ЦветФонаЗаголовка = WebЦвета[Объект.Помещение.Цвет];
	КонецЕсли;
	
	Если ЗначениеЗаполнено(Объект.ПредметОбучения) и ЗначениеЗаполнено(Объект.ПредметОбучения.Цвет) Тогда
		Элементы.ПредметОбучения.ЦветФонаЗаголовка = WebЦвета[Объект.ПредметОбучения.Цвет];
	КонецЕсли;
	
КонецПроцедуры

Функция РассчитатьЗадолженность(Ученик, ПредметОбучения, Организация)
	
	Если ПредметОбучения <> Неопределено Тогда 
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	СписанияСуммЗаУрокиОстатки.СуммаОстаток КАК СуммаОстаток
		|ИЗ
		|	РегистрНакопления.LM_СписанияСуммЗаУроки.Остатки КАК СписанияСуммЗаУрокиОстатки
		|ГДЕ
		|	СписанияСуммЗаУрокиОстатки.ПредметОбучения = &ПредметОбучения
		|	И СписанияСуммЗаУрокиОстатки.Клиент = &Клиент
		|	И СписанияСуммЗаУрокиОстатки.Организация = &Организация"; 		
		Запрос.УстановитьПараметр("ПредметОбучения", ПредметОбучения);
	Иначе
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	СписанияСуммЗаУрокиОстатки.СуммаОстаток КАК СуммаОстаток
		|ИЗ
		|	РегистрНакопления.LM_СписанияСуммЗаУроки.Остатки КАК СписанияСуммЗаУрокиОстатки
		|ГДЕ
		|	СписанияСуммЗаУрокиОстатки.Клиент = &Клиент
		|	И СписанияСуммЗаУрокиОстатки.Организация = &Организация";   	
	КонецЕсли;	
	Запрос.УстановитьПараметр("Клиент", Ученик);
	Запрос.УстановитьПараметр("Организация", Организация);
	РезультатЗапроса = Запрос.Выполнить(); 	
	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();	
	
	Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
		Возврат ВыборкаДетальныеЗаписи.СуммаОстаток;
	КонецЦикла;	
	
	Возврат 0;
	
КонецФункции
Функция РассчитатьОстатокБонусов(Ученик, ДисконтнаяКарта, Организация)
	
	Если НЕ ЗначениеЗаполнено(Ученик) или НЕ ЗначениеЗаполнено(ДисконтнаяКарта) Тогда
		Возврат 0;
	КонецЕсли;
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	ДвижениеДисконтныхКарт.СуммаБонусовОстаток КАК СуммаБонусовОстаток
	|ИЗ
	|	РегистрНакопления.LM_ДвижениеДисконтныхКарт.Остатки КАК ДвижениеДисконтныхКарт
	|ГДЕ
	|	ДвижениеДисконтныхКарт.Клиент = &Клиент
	|	И ДвижениеДисконтныхКарт.ДисконтнаяКарта = &ДисконтнаяКарта
	|	И ДвижениеДисконтныхКарт.Организация = &Организация";   	
	
	Запрос.УстановитьПараметр("Клиент", Ученик);
	Запрос.УстановитьПараметр("Организация", Организация);
	Запрос.УстановитьПараметр("ДисконтнаяКарта", ДисконтнаяКарта);
	РезультатЗапроса = Запрос.Выполнить(); 	
	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();	
	
	Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
		Возврат ВыборкаДетальныеЗаписи.СуммаБонусовОстаток;
	КонецЦикла;	
	
	Возврат 0;
	
КонецФункции

&НаКлиенте
Процедура ПриЗакрытии(ЗавершениеРаботы)
	Оповестить("ЗакрытьФормуУрока");
КонецПроцедуры

&НаКлиенте
Процедура УченикиСписатьОплатуПриИзменении(Элемент)		
	ПересчитатьТабличнуюЧасть();
	ПересчитатьНачисленияПедагога(Ложь);
	ОбновитьВидимость();
КонецПроцедуры

&НаКлиенте
Процедура Подбор(Команда)
	
	ОП = Новый ОписаниеОповещения("ПодборУчениковЗавершение",ЭтотОбъект);
	ПП = Новый Структура("МножественныйВыбор",Истина);
	Отбор = Новый Структура("Родитель",ВернутьПапкуУченики());
	ПП.Вставить("Отбор", Отбор); 
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаВыбора",ПП,ЭтотОбъект,,,,ОП,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);
	
	//ОткрытьФорму("Справочник.ФизЛица.Форма.ФормаПодбора",,Элементы.Ученики,ЭтаФорма.УникальныйИдентификатор);
	
КонецПроцедуры
Функция ВернутьПапкуУченики()
	Возврат Справочники.LM_ФизЛица.Ученики.Ссылка;
КонецФункции

&НаКлиенте
Процедура ПодборУчениковЗавершение(Результат,Параметры) Экспорт 
	Если Результат <> Неопределено Тогда
		Для Каждого Ученик Из Результат Цикл
			НоваяСтрока = Объект.Ученики.Добавить();
			НоваяСтрока.Ученик = Ученик;
		КонецЦикла;
	КонецЕсли;
КонецПроцедуры

Процедура ДобавитьВыбранных(Массив)
	
	Попытка 
		Для Каждого Стр из Массив Цикл
			НовСтр = Объект.Ученики.Добавить();
			НовСтр.Ученик = Стр;  
		КонецЦикла;
	Исключение
	КонецПопытки;
	
КонецПроцедуры 

&НаКлиенте
Процедура УченикиОбработкаВыбора(Элемент, ВыбранноеЗначение, СтандартнаяОбработка)
	
	ДобавитьВыбранных(ВыбранноеЗначение);
	
	ПересчитатьТабличнуюЧасть();
	
КонецПроцедуры

&НаКлиенте
Процедура ПлатныйПриИзменении(Элемент)
	ПересчитатьТабличнуюЧасть();	
КонецПроцедуры

&НаКлиенте
Процедура УченикиУченикПриИзменении(Элемент)
	
	Если ЗначениеЗаполнено(Элементы.Ученики.ТекущиеДанные.Ученик) Тогда
		Элементы.Ученики.ТекущиеДанные.ДисконтнаяКарта = НайтиДисконтнуюКарту(Элементы.Ученики.ТекущиеДанные.Ученик);
	КонецЕсли;
	
КонецПроцедуры

Функция НайтиДисконтнуюКарту(Ученик) 
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
	"ВЫБРАТЬ
	|	ДисконтныеКарты.Ссылка КАК Ссылка
	|ИЗ
	|	Справочник.LM_ДисконтныеКарты КАК ДисконтныеКарты
	|ГДЕ
	|	ДисконтныеКарты.Владелец = &Владелец
	|	И ДисконтныеКарты.ДатаОкончанияДействия > &ДатаОкончанияДействия
	|	И ДисконтныеКарты.ПометкаУдаления = ЛОЖЬ"; 	
	Запрос.УстановитьПараметр("Владелец", Ученик);
	Запрос.УстановитьПараметр("ДатаОкончанияДействия", ?(ЗначениеЗаполнено(Объект.Дата),КонецДня(Объект.Дата),КонецДня(ТекущаяДата())));	
	РезультатЗапроса = Запрос.Выполнить().Выгрузить();
	
	Если РезультатЗапроса.Количество()=1 Тогда
		Возврат РезультатЗапроса[0].Ссылка;
	КонецЕсли;
	
	Возврат Неопределено;
	
КонецФункции

&НаКлиенте
Процедура УченикиУченикСоздание(Элемент, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	ПараметрыСтроки = Новый Структура;
	
	Назв = СокрЛП(Элемент.ТекстРедактирования);
	
	Если Найти(Назв," ") > 0 Тогда
		Симв1 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Фамилия",Лев(Назв,Симв1-1));
		Назв = СокрЛП(Сред(Назв,Симв1+1));
	Иначе
		ПараметрыСтроки.Вставить("Фамилия",Назв);
		Назв = "";
	КонецЕсли;
	
	Если (Найти(Назв," ") > 0) и (СтрДлина(Назв) > 0) Тогда
		Симв2 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Имя",Лев(Назв,Симв2-1));
		Назв = СокрЛП(Сред(Назв,Симв2+1));
	Иначе
		ПараметрыСтроки.Вставить("Имя",Назв);
		Назв = "";
	КонецЕсли;
	
	Если СтрДлина(Назв) > 0 Тогда
		ПараметрыСтроки.Вставить("Отчество",Назв);
	КонецЕсли;
	
	ПараметрыСтроки.Вставить("Группа","Ученики");
	
	Пар = Новый Структура("Ключ2", ПараметрыСтроки);
	
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаЭлемента",Пар,ЭтотОбъект,ЭтаФорма.УникальныйИдентификатор,ВариантОткрытияОкна.ОтдельноеОкно,,,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);
	
КонецПроцедуры

&НаКлиенте
Процедура ГруппаОбученияПриИзменении(Элемент)
	
	ГруппаОбученияПриИзмененииНаСервере();
	
	ПересчитатьТабличнуюЧасть();
	
КонецПроцедуры
Процедура ГруппаОбученияПриИзмененииНаСервере()
	
	Если ЗначениеЗаполнено(Объект.ГруппаОбучения) Тогда
		Объект.Педагог 			= Объект.ГруппаОбучения.Педагог;
		Объект.Помещение 		= Объект.ГруппаОбучения.Помещение;
		Объект.КоличествоЧасов 	= Объект.ГруппаОбучения.Продолжительность;
		Объект.ПредметОбучения 	= Объект.ГруппаОбучения.ПредметОбучения;
		//Элементы.Педагог.ТолькоПросмотр				= Истина;
		//Элементы.КоличествоЧасов.ТолькоПросмотр 	= Истина;
		//Элементы.ПредметОбучения.ТолькоПросмотр 	= Истина;
		//Элементы.Помещение.ТолькоПросмотр 			= Истина;
	Иначе
		//Объект.Педагог 			= Неопределено;
		//Объект.Помещение 		= Неопределено;
		//Объект.КоличествоЧасов 	= Неопределено;
		//Объект.ПредметОбучения 	= Неопределено;
		//Элементы.Педагог.ТолькоПросмотр 			= Ложь;
		//Элементы.КоличествоЧасов.ТолькоПросмотр 	= Ложь;
		//Элементы.ПредметОбучения.ТолькоПросмотр 	= Ложь;
		//Элементы.Помещение.ТолькоПросмотр 			= Ложь;
	КонецЕсли;
	
КонецПроцедуры 

&НаКлиенте
Процедура УченикиКоэффициентОчистка(Элемент, СтандартнаяОбработка)
	ПересчитатьТабличнуюЧасть();
КонецПроцедуры

Процедура ПриЧтенииНаСервере(ТекущийОбъект)
	ДатыЗапретаИзменения.ОбъектПриЧтенииНаСервере(ЭтотОбъект, ТекущийОбъект)
КонецПроцедуры

&НаКлиенте
Процедура УченикиВыбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)
	
	Если Поле.Имя = "УченикиЗадолженностьПоПредмету" Тогда
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Элементы.Ученики.ТекущиеДанные.Ученик);
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	ИначеЕсли Поле.Имя = "УченикиЗадолженностьОбщая" Тогда
		ПараметрыОткрытия = ОткрытьВзаиморасчетыНаСервере(Элементы.Ученики.ТекущиеДанные.Ученик);
		ОткрытьФорму("Отчет.LM_Взаиморасчеты.Форма", ПараметрыОткрытия, ЭтаФорма);
	ИначеЕсли Поле.Имя = "Ученики1ОстатокБонусов" Тогда
		ОткрытьФорму("Отчет.LM_ОтчетПоДисконтнымКартам.Форма", , ЭтаФорма);	
	КонецЕсли;
	
КонецПроцедуры

Функция ОткрытьВзаиморасчетыНаСервере(Ученик)
	
	КомпоновщикНастроек = Отчеты.LM_Взаиморасчеты.Создать().КомпоновщикНастроек; 
	Настройки 			= КомпоновщикНастроек.Настройки; 
	
	//ЭлементНастройки = Настройки.ПараметрыДанных.НайтиЗначениеПараметра(Новый ПараметрКомпоновкиДанных("Период")); 
	////ЭлементНастройки.Значение.ДатаНачала    = '00010101';//НачалоГода(ТекущаяДата());
	////ЭлементНастройки.Значение.ДатаОкончания = '00010101';//КонецГода(ТекущаяДата());
	//Если ЗначениеЗаполнено(ЭлементНастройки.ИдентификаторПользовательскойНастройки) Тогда 
	//	ПользовательскийПараметр = КомпоновщикНастроек.ПользовательскиеНастройки.Элементы.Найти(ЭлементНастройки.ИдентификаторПользовательскойНастройки); 
	//	Если ТипЗнч(ПользовательскийПараметр) = Тип("ЗначениеПараметраНастроекКомпоновкиДанных") Тогда 
	//		//ПользовательскийПараметр.Значение = ЭлементНастройки.Значение;
	//		ПользовательскийПараметр.Использование = Ложь;
	//	КонецЕсли; 
	//КонецЕсли; 
	
	ОтборУченик = Новый ПолеКомпоновкиДанных("Клиент");
	
	Для Каждого ЭлементНастройки Из Настройки.Отбор.Элементы Цикл 
		Если ЭлементНастройки.ЛевоеЗначение = ОтборУченик Тогда 
			ЭлементНастройки.ВидСравнения = ВидСравненияКомпоновкиДанных.Равно; 
			ЭлементНастройки.ПравоеЗначение = Ученик; 
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

Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	
	Если Параметры.Свойство("Дата") Тогда
		Дата = Параметры.Дата;
	КонецЕсли;	
	
	LMНастроки = РегистрыСведений.LM_Настройки.ПолучитьПоследнее(ТекущаяДата());
	Если LMНастроки.Свойство("ДатаЗапретаРедактирования") Тогда
	//Если ЗначениеЗаполнено(Объект.Организация) и ЗначениеЗаполнено(Объект.Организация.LM_ДатаЗапретаРедактирования) Тогда
		ДатаЗапрета = LMНастроки.ДатаЗапретаРедактирования;
		Если Объект.Проведен и ЗначениеЗаполнено(ДатаЗапрета) Тогда
			Если Объект.Дата <= ДатаЗапрета	Тогда
				Для Каждого Элем из ЭтаФорма.Элементы Цикл				
					Попытка
						Элем.ТолькоПросмотр = Истина;			
					Исключение
					КонецПопытки;
				КонецЦикла;
				
			КонецЕсли; 		
		КонецЕсли;
	КонецЕсли;
	
	Если ЗначениеЗаполнено(Объект.Дата) Тогда
		ОбновитьВидимость();
	КонецЕсли;
	
	Если Найти(Метаданные.Имя,"LessonsManagement") = 0 Тогда
		Элементы.УченикиПодбор.Видимость = Ложь;
	КонецЕсли;
		
КонецПроцедуры

&НаКлиенте
Процедура ШтрихкодПриИзменении(Элемент)
	НайтиПоШК();
КонецПроцедуры

Процедура НайтиПоШК()
	
	Если ЗначениеЗаполнено(Штрихкод) Тогда
		
		Для Каждого Стр из Объект.Ученики Цикл
			Если Стр.Ученик = Штрихкод.Владелец Тогда
				Стр.ДисконтнаяКарта = Штрихкод;	
			КонецЕсли; 			
		КонецЦикла;
		
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура НайтиПоШККоманда(Команда)
	НайтиПоШК();
КонецПроцедуры

//&НаКлиенте
//Процедура ОткрытьПодборПоУченику()
//	
//	Владелец = Элементы.Ученики1.ТекущиеДанные.Ученик;
//	ЗначениеОтбора = Новый Структура("Владелец", Владелец);
//	ПараметрыВыбора1 = Новый Структура("Отбор", ЗначениеОтбора);
//	
//	ОткрытьФорму("Справочник.LM_ДисконтныеКарты.ФормаВыбора", ПараметрыВыбора1, ЭтотОбъект);
//	
//КонецПроцедуры

&НаКлиенте
Процедура Ученики1ДисконтнаяКартаНачалоВыбора(Элемент, ДанныеВыбора, СтандартнаяОбработка)	
	СтандартнаяОбработка = Ложь;
	ПараметрыОтбора = Новый Структура("Владелец", Элементы.Ученики.ТекущиеДанные.Ученик); 
	ПараметрыОткрытия = Новый Структура("Отбор", ПараметрыОтбора); 
	ОткрытьФорму("Справочник.LM_ДисконтныеКарты.ФормаВыбора", ПараметрыОткрытия, Элемент, ЭтаФорма);
КонецПроцедуры

&НаКлиенте
Процедура КоличествоЧасовПриИзменении(Элемент)
	ПересчитатьТабличнуюЧасть();
КонецПроцедуры

&НаКлиенте
Процедура УченикиЧасыПриИзменении(Элемент)
	ПересчитатьТабличнуюЧасть();
КонецПроцедуры


&НаКлиенте
Процедура ПередЗаписью(Отказ, ПараметрыЗаписи)
	
	Если ПараметрыЗаписи.РежимЗаписи = РежимЗаписиДокумента.Проведение и ЗначениеЗаполнено(Объект.Педагог) Тогда
		
		НомерБезНулей = Объект.Номер;
		Пока Найти(НомерБезНулей,"0") = 1 Цикл
			НомерБезНулей = Сред(НомерБезНулей,2); //удаляет лидирующие нули
		КонецЦикла;
			
		ИтогПроверки = ПроверитьДокументПоГрафикуРабочегоВремени();
		
		Если ИтогПроверки <> Неопределено Тогда 			
			
			ТекстОповещения = "Урок №"+НомерБезНулей+ " от " +Формат(Объект.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Объект.Дата,"ДФ=HH:mm")+ 
			" по " +Формат(Объект.Дата-('00010101'-Объект.КоличествоЧасов),"ДФ=HH:mm") + " не входит в график учета рабочего времени педагога " 
			+ИтогПроверки.Педагог+ " (" +Формат(ИтогПроверки.Дата,"ДФ='ММММ гггг ""г"".'")+ ")!!!";
			
			Режим = РежимДиалогаВопрос.ДаНет;
			Ответ = Вопрос(ТекстОповещения + Символы.ПС + "Продолжить запись урока?", Режим, 0);
			Если Ответ = КодВозвратаДиалога.Нет Тогда
				Отказ = Истина;
			КонецЕсли;
			
		КонецЕсли;
		
		ДокументПересечения = ДокументПересекаетсяСДругими();
		Если ДокументПересечения <> Неопределено Тогда
			
			Режим = РежимДиалогаВопрос.ДаНет;
			
	        НомерБезНулей2 = ДокументПересечения.Номер;
			Пока Найти(НомерБезНулей2,"0") = 1 Цикл
				НомерБезНулей2 = Сред(НомерБезНулей2,2); //удаляет лидирующие нули
			КонецЦикла;
			
			Ответ = Вопрос("Урок №"+НомерБезНулей+ " от " +Формат(Объект.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Объект.Дата,"ДФ=HH:mm")+ 
			" по " +Формат(Объект.Дата-('00010101'-Объект.КоличествоЧасов),"ДФ=HH:mm")+ " пересекается по времени с уроком №"+НомерБезНулей2+ 
			" с " +Формат(ДокументПересечения.Дата,"ДФ=HH:mm")+	" по " +Формат(ДокументПересечения.Дата-('00010101'-ДокументПересечения.КоличествоЧасов),"ДФ=HH:mm")
			+ ?(Объект.Педагог = ДокументПересечения.Педагог, Символы.ПС+ "по педагогу: " +ДокументПересечения.Педагог+ "!!!","")
			+ ?(Объект.Помещение = ДокументПересечения.Помещение, Символы.ПС+ "по помещению: " +ДокументПересечения.Помещение+ "!!!","") 
			+ Символы.ПС+ "Продолжить запись урока?", Режим, 0);
			Если Ответ = КодВозвратаДиалога.Нет Тогда
				Отказ = Истина;
			КонецЕсли;

		КонецЕсли;    

	КонецЕсли;  	

КонецПроцедуры

Функция ПроверитьДокументПоГрафикуРабочегоВремени()	
	Возврат Документы.LM_Урок.ПроверитьДокументПоГрафикуРабочегоВремени(Объект);	
КонецФункции 
Функция ДокументПересекаетсяСДругими()	
	Возврат Документы.LM_Урок.ДокументПересекаетсяСДругими(Объект);	
КонецФункции

&НаКлиенте
Процедура ДатаПриИзменении(Элемент)
	ПересчитатьТабличнуюЧасть();
КонецПроцедуры

&НаКлиенте
Процедура ДвиженияДокумента(Команда)
	
	С = Новый Структура;
	С.Вставить("Документ",Объект.Ссылка);
	ОткрытьФорму("Отчет.LM_ДвиженияДокумента.Форма.ДвиженияДокумента",С ,ЭтаФорма, , , , ,РежимОткрытияОкнаФормы.Независимый);
	
КонецПроцедуры

&НаКлиенте
Процедура ПересчитатьНачисления(Команда)
	ПересчитатьНачисленияПедагога(Ложь);
	ОбновитьВидимость();
КонецПроцедуры
Процедура ПересчитатьНачисленияПедагога(ПолныйПересчет)
	Документы.LM_Урок.ПересчитатьНачисленияПедагога(Объект,ПолныйПересчет);
КонецПроцедуры

&НаКлиенте
Процедура ИзменятьВсе(Команда)
	Для Каждого Стр из Объект.НачисленияПедагогу Цикл
		Стр.НеИзменять = Ложь;
	КонецЦикла;	
КонецПроцедуры 
&НаКлиенте
Процедура НеИзменятьВсе(Команда)
	Для Каждого Стр из Объект.НачисленияПедагогу Цикл
		Стр.НеИзменять = Истина;
	КонецЦикла;	
КонецПроцедуры

&НаКлиенте
Процедура ПедагогПриИзменении(Элемент)	
	ПедагогПриИзмененииНаСервере();	
	ОбновитьВидимость();
КонецПроцедуры
Процедура ПедагогПриИзмененииНаСервере()
	
	Объект.НачисленияПедагогу.Очистить();
	
	Если ЗначениеЗаполнено(Объект.Педагог) Тогда
		Объект.СтавкаПедагога = Объект.Педагог.СтавкаПедагога;
	Иначе                                    		
		Объект.СтавкаПедагога = Справочники.LM_СтавкиПедагогов.ПустаяСсылка();
	КонецЕсли;
	
	ПересчитатьНачисленияПедагога(Истина);
	
КонецПроцедуры

&НаКлиенте
Процедура СтавкаПедагогаПриИзменении(Элемент)	
	ПересчитатьНачисленияПедагога(Истина);
	ОбновитьВидимость();
КонецПроцедуры  

&НаКлиенте
Процедура НачисленияПедагогуПриИзменении(Элемент)
	ОбновитьВидимость();
КонецПроцедуры
