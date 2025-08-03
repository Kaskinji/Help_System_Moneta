comcore_R_ontology = '''
comcore:isResultOf rdf:type owl:ObjectProperty;
  owl:inverseOf comcore:hasResult;
  rdf:type owl:IrreflexiveProperty;
  rdfs:label "результат"@ru;
  rdfs:label "result"@en;
  rdfs:domain comcore:Resource;
  rdfs:domain comcore:Event;
  rdfs:range comcore:Process;
  rdfs:comment """
Указывает что Событие или Ресурс (субъект) является результатом Процесса (объект).
Пример: Регистрация в форме может закончиться неуспешно если ИНН или Email уже зарегистрирован.
Субъекты: Успешная регистрация, ИНН уже зарегистрирован, Email уже зарегистрирован.""".

comcore:canBeResourceFor rdf:type owl:ObjectProperty;
  rdfs:label "может быть Ресурсом"@ru;
  rdfs:label "может использоваться как Ресурс в"@ru;
  rdfs:label "can be resource for"@en;
  rdfs:label "can be resource in"@en;
  rdfs:domain comcore:Resource;
  rdfs:range comcore:Process;
  rdfs:comment """Указывает что Ресурс (субъект) может использоваться в качестве входного Ресурса данного Процесса (объект). Например, ответ на секретный вопрос может использоваться при аутентификации""" .

comcore:isResourceOf rdf:type owl:ObjectProperty;
  owl:inverseOf comcore:hasResource;
  rdfs:label "является Ресурсом"@ru;
  rdfs:label "is Resource of"@en;
  rdfs:domain comcore:Resource;
  rdfs:range comcore:Process;
  rdfs:comment """Указывает что Ресурс (субъект) является необходимым входным Ресурсом данного Процесса (объект). Например, логин или пароль при аутентификации""" .

comcore:isActorOf rdf:type owl:ObjectProperty;
  owl:inverseOf comcore:hasActor;
  rdfs:label "является Актором"@ru;
  rdfs:label "is Actor of"@en;
  rdfs:comment "Указывает Агента (субъект), который в какой-то роли принимает участие в Процессе (объект)";
  rdfs:domain comcore:Agent;
  rdfs:range comcore:Process.

comcore:Initiates rdfs:subPropertyOf comcore:;
  rdfs:label "инициирует"@ru;
  rdfs:label "initiates"@en;
  rdfs:comment "Указывает что субъект инициирует данный Процесс.";
  rdfs:domain comcore:Event;
  rdfs:domain comcore:Agent;
  rdfs:range comcore:Process.

comcore:isPartOf rdfs:subPropertyOf dcterms:isPartOf;
  owl:inverseOf comcore:hasPart;
  rdf:type owl:IrreflexiveProperty;
  rdf:type owl:TransitiveProperty;
  rdfs:label "является частью"@ru;
  rdfs:label "is part of"@en;
  rdfs:domain comcore:Process;
  rdfs:domain comcore:Resource;
  rdfs:range comcore:Process;
  rdfs:range comcore:Resource;
  rdfs:comment "Указывает, что субъект является частью для данного объекта".

comcore:isResponsibleFor rdfs:subPropertyOf dcterms:contributor;
  rdfs:label "ответственный"@ru;
  rdfs:label "responsible"@en;
  rdfs:comment "Указывает, что Агент (субъект) отвечает за наличие/создание данного Ресурса (объект) или является ответственным за проведение Процесса";
  rdfs:domain comcore:Agent;
  rdfs:range comcore:Resource;
  rdfs:range comcore:Process.

comcore:relation rdfs:subPropertyOf dcterms:relation;
  rdf:type owl:IrreflexiveProperty;
  rdfs:label "связан с"@ru;
  rdfs:label "relation"@en;
  rdfs:comment "Указывает, что одна сущность (субъект) как-то связана с другой сущностью (объект). Отношение используется, если не подходят вышеперечисленные отношения".
'''