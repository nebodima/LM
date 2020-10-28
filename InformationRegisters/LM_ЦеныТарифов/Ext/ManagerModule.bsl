﻿Функция ПолучитьСуммуТарифаНаДату(Тариф, Дата) Экспорт
	
	С = новый Структура;
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
		"ВЫБРАТЬ
		|	ЦеныТарифовСрезПоследних.Сумма КАК Сумма,
		|	ЦеныТарифовСрезПоследних.КоличествоЧасов КАК КоличествоЧасов,
		|	ЦеныТарифовСрезПоследних.КоличествоЗанятий КАК КоличествоЗанятий
		|ИЗ
		|	РегистрСведений.LM_ЦеныТарифов.СрезПоследних(&Период, Тариф = &Тариф) КАК ЦеныТарифовСрезПоследних";  	
	Запрос.УстановитьПараметр("Период", Дата);
	Запрос.УстановитьПараметр("Тариф", Тариф);
	РезультатЗапроса = Запрос.Выполнить().Выгрузить();
	
	Если РезультатЗапроса.Количество() = 1 Тогда
		
		Если РезультатЗапроса[0].КоличествоЗанятий > 0 Тогда
			С.Вставить("КоличествоЗанятий",РезультатЗапроса[0].КоличествоЗанятий);
		Иначе			
			С.Вставить("КоличествоЧасов",РезультатЗапроса[0].КоличествоЧасов);
		КонецЕсли;
		С.Вставить("Сумма",РезультатЗапроса[0].Сумма);
		
		Возврат С;
		
	КонецЕсли;

	Возврат Неопределено;
	
КонецФункции
