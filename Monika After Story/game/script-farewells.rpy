##This file contains all of the variations of goodbye that monika can give.
## This also contains a store with a utility function to select an appropriate
## farewell
#
# HOW FAREWELLS USE EVENTS:
#   unlocked - determines if the farewell can actually be shown
#   random - True means the farewell is shown in the randomly selected
#       goodbye option
#   pool - True means the farewell is shown in the goodbye list. Prompt
#       is used in this case.

#Flag to mark if the player stayed up late last night. Kept as a generic name in case it can be used on other farewells/greetings
default persistent.mas_late_farewell = False

init -1 python in mas_farewells:

    # custom farewell functions
    def selectFarewell():
        """
        Selects a farewell to be used. This evaluates rules and stuff
        appropriately.

        RETURNS:
            a single farewell (as an Event) that we want to use
        """

        # check if we have moni_wants farewells
        moni_wants_farewells = renpy.store.Event.filterEvents(
            renpy.store.evhand.farewell_database,
            unlocked=True,
            pool=False, # may as well not filter these
            moni_wants=True
        )


        if moni_wants_farewells is not None and len(moni_wants_farewells) > 0:

            # select one label randomly
            return moni_wants_farewells[
                renpy.random.choice(moni_wants_farewells.keys())
            ]

        # now filter events by their unlocked property
        unlocked_farewells = renpy.store.Event.filterEvents(
            renpy.store.evhand.farewell_database,
            unlocked=True,
            pool=False
        )

        # filter farewells using the affection rules dict
        unlocked_farewells = renpy.store.Event.checkAffectionRules(
            unlocked_farewells,
            keepNoRule=True
        )

        # filter farewells using the special rules dict
        random_farewells_dict = renpy.store.Event.checkRepeatRules(
            unlocked_farewells
        )

        # check if we have a farewell that actually should be shown now
        if len(random_farewells_dict) > 0:

            # select one label randomly
            return random_farewells_dict[
                renpy.random.choice(random_farewells_dict.keys())
            ]

        # since we don't have special farewells for this time we now check for special random chance
        # pick a farewell filtering by special random chance rule
        random_farewells_dict = renpy.store.Event.checkFarewellRules(
            unlocked_farewells
        )

        # check if we have a farewell that actually should be shown now
        if len(random_farewells_dict) > 0:

            # select on label randomly
            return random_farewells_dict[
                renpy.random.choice(random_farewells_dict.keys())
            ]

        # We couldn't find a suitable farewell we have to default to normal random selection
        # filter random events normally
        random_unlocked_farewells = renpy.store.Event.filterEvents(
            unlocked_farewells,
            random=True
        )

        # check if we have farewell available to display with current filter
        if len(random_unlocked_farewells) > 0:
            # select one randomly
            return random_unlocked_farewells[
               renpy.random.choice(random_unlocked_farewells.keys())
            ]

        # We couldn't find a suitable farewell we have to default to normal random selection
        # filter random events normally
        renpy.log("rip we need update script")
        random_farewells_dict = renpy.store.Event.filterEvents(
            renpy.store.evhand.greeting_database,
            unlocked=True,
            random=True,
            excl_cat=list()
        )

        # select one randomly
        return random_farewells_dict[
            renpy.random.choice(random_farewells_dict.keys())
        ]

# farewells selection label
label mas_farewell_start:
    # TODO: if we ever have another special farewell like long absence
    # that let's the player go after selecting the farewell we'll need
    # to define a system to handle those.
    if persistent._mas_long_absence:
        $ pushEvent("bye_long_absence_2")
        return

    $ import store.evhand as evhand
    # we use unseen menu values

    python:
        # preprocessing menu
        # TODO: consider including processing the rules dict as well
        bye_pool_events = Event.filterEvents(
            evhand.farewell_database,
            unlocked=True,
            pool=True
        )

    if len(bye_pool_events) > 0:
        # we have selectable options
        python:
            # build a prompt list
            bye_prompt_list = [
                (ev.prompt, ev, False, False)
                for k,ev in bye_pool_events.iteritems()
            ]

            # add the random selection
            bye_prompt_list.append(("Goodbye.", -1, False, False))

            # setup the last option
            bye_prompt_back = ("Nevermind.", False, False, False, 20)

        # call the menu
        call screen mas_gen_scrollable_menu(bye_prompt_list, evhand.UNSE_AREA, evhand.UNSE_XALIGN, bye_prompt_back)

        if not _return:
            # user its nevermind
            return

        if _return != -1:
            # push teh selected event
            $ pushEvent(_return.eventlabel)
            return

    # otherwise, select a random farewell
    $ farewell = store.mas_farewells.selectFarewell()
    $ pushEvent(farewell.eventlabel)
    # dont evalulate the mid loop checks since we are quitting
    $ mas_idle_mailbox.send_skipmidloopeval()

    return

###### BEGIN FAREWELLS ########################################################
## FARE WELL RULES:
# unlocked - True means this farewell is ready for selection
# random - randoms are used in teh default farewell action
# pool - pooled ones are selectable in the menu
# rules - Dict containing different rules(check event-rules for more details)
###

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=-29,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_leaving_already",
            unlocked=True,
            random=True,#TODO update script
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_leaving_already:
    m 1tkc "Aw, leaving already?"
    m 1eka "It's really sad whenever you have to go..."
    m 3eua "Just be sure to come back as soon as you can, okay?"
    m "I love you so much, [player]. Stay safe!"
    #Don't show this farewell again
    $evhand.farewell_database["bye_leaving_already"].random=False
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodbye",
            unlocked=True,
            random=True
        ),
        code="BYE"
    )

label bye_goodbye:
    if mas_isMoniNormal(higher=True):
        m 1eua "Goodbye, [player]!"

    elif mas_isMoniUpset():
        m 2efc "Goodbye."

    elif mas_isMoniDis():
        m 6rkc "Oh...{w=1} Goodbye."
        m 6ekc "Please...{w=1}don't forget to come back."

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=-29,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_sayanora",#sayanora? yes
            unlocked=True,
            random=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_sayanora:
    m 1hua "Sayonara, [player]~"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=-29,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_farewellfornow",
            unlocked=True,
            random=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_farewellfornow:
    m 1eka "Farewell for now, my love~"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=-29,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_untilwemeetagain",
            unlocked=True,
            random=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_untilwemeetagain:
    m 2eka "'{i}Goodbyes are not forever, Goodbyes are not the end. They simply mean I'll miss you, Until we meet again.{/i}'"
    m "Ehehe, 'till then, [player]!"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=-29,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_take_care",
            unlocked=True,
            random=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules


label bye_take_care:
    m 1eua "Don't forget that I always love you, [player]~"
    m 1hub "Take care!"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(21,24)))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_going_to_sleep",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_going_to_sleep:
    if mas_isMoniNormal(higher=True):
        m 1esa "Are you going to sleep, [player]?"
        m 1eka "I'll be seeing you in your dreams."

    elif mas_isMoniUpset():
        m 2efc "Going to sleep, [player]?"
        m 2esc "Goodnight."

    elif mas_isMoniDis():
        m 6rkc "Oh...goodnight, [player]."
        m 6lkc "Hopefully I'll see you tomorrow..."
        m 6dkc "Don't forget about me, okay?"

    else:
        m 6ckc "..."

    # TODO:
    # can monika sleep with you?
    # via flashdrive or something

    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_to_class",
            unlocked=True,
            prompt="I'm going to class.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_to_class:
    $ session_time = mas_getSessionLength()
    if mas_isMoniNormal(higher=True):
        if session_time < datetime.timedelta(minutes=20):
            m 1eub "Aw, going already?"
            m 1efp "You haven't even been here for 20 minutes!"
            m 3hksdlb "I'm just kidding, [player]."
            m 2eka "You're so sweet for seeing me even when you have so little time."
            m 2hub "I just want you to know I really appreciate that!"
            m 2eka "Study hard [player], I'm sure you'll do great!"
            m 2hua "See you when you get back!"
        elif session_time < datetime.timedelta(hours=1):
            m 2eua "Alright, thanks for spending some time with me, [player]!"
            m 2eka "I honestly wish it could have been longer...but you're a busy [guy]."
            m 2hua "Nothing is more important than a good education."
            m 3eub "Teach me something when you get back!"
            m "See you soon!"
        elif session_time < datetime.timedelta(hours=6):
            m 1hua "Study hard, [player]!"
            m 1eua "Nothing is more attractive than a [guy] with good grades."
            m 1hua "See you later!"
        else:
            m 2ekc "Umm...you've been here with me for quite a while, [player]."
            m 2ekd "Are you sure you've had enough rest for it?"
            m 2eka "Make sure you take it easy, okay?"
            m "If you're not feeling too well, I'm sure {i}one day{/i} off won't hurt."
            m 1hka "I'll be waiting for you to come back. Stay safe."

    elif mas_isMoniUpset():
        m 2efc "Fine, [player]."
        m 2tfc "Hopefully you at least learn something today."
        m "{cps=*2}Like how to treat people better.{/cps}{nw}"

    elif mas_isMoniDis():
        m 6rkc "Oh, okay [player]..."
        m 6lkc "I guess I'll see you after school."

    else:
        m 6ckc "..."
    # TODO:
    # can monika join u at schools?
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SCHOOL
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_to_work",
            unlocked=True,
            prompt="I'm going to work.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_to_work:
    $ session_time = mas_getSessionLength()
    if mas_isMoniNormal(higher=True):
        if session_time < datetime.timedelta(minutes=20):
            m 2eka "Aw, okay! Just checking in on me before heading out?"
            m 3eka "You must be really short on time if you're leaving already."
            m "It was really sweet of you to see me, even when you're so busy!"
            m 3hub "Work hard, [player]! Make me proud!"
        elif session_time < datetime.timedelta(hours=1):
            m 1hksdlb "Oh! Alright! I was starting to get really comfortable, ahaha."
            m 1rusdlb "I was expecting us to be a here a bit longer, but you're a busy [guy]!"
            m 1eka "It was great seeing you, even if it wasn't as long as I wanted..."
            m 1kua "But then if it were up to me I'd have you all day!"
            m 1hua "I'll be here waiting for you to get back home from work!"
            m "Tell me all about it when you get back!"
        elif session_time < datetime.timedelta(hours=6):
            m 2eua "Heading to work then, [player]?"
            m 2eka "The day may be good or bad...but if it becomes too much think of something nice!"
            m 4eka "Every day, no matter how badly it's going ends after all!"
            m 2tku "Maybe you can think of me if it becomes stressful..."
            m 2esa "Just do your best! I'll see you when you get back!"
            m 2eka "I know you'll do great!"
        else:
            m 2ekc "Oh... You've been here quite a while now...and now you're going to work?"
            m 2rksdlc "I was hoping you'd rest before doing anything too big."
            m 2ekc "Try not to overexert yourself, okay?"
            m 2ekd "Don't be afraid to take a breather if you need to!"
            m 3eka "Just come home to me happy and healthy."
            m 3eua "Stay safe, [player]!"

    elif mas_isMoniUpset():
        m 2efc "Fine, [player], guess I'll see you after work."

    elif mas_isMoniDis():
        m 6rkc "Oh...{w=1} Okay."
        m 6lkc "Hopefully I'll see you after work, then."

    else:
        m 6ckc "..."
    # TODO:
    # can monika join u at work
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_WORK
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_sleep",
            unlocked=True,
            prompt="I'm going to sleep.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_sleep:

    python:
        import datetime
        curr_hour = datetime.datetime.now().hour

    # these conditions are in order of most likely to happen with our target
    # audience

    if 20 <= curr_hour < 24:
        # decent time to sleep
        if mas_isMoniNormal(higher=True):
            m 1eua "Alright, [player]."
            m 1hua "Sweet dreams!"

        elif mas_isMoniUpset():
            m 2efc "Goodnight, [player]."

        elif mas_isMoniDis():
            m 6ekc "Okay...{w=1} Goodnight, [player]."

        else:
            m 6ckc "..."

    elif 0 <= curr_hour < 3:
        # somewhat late to sleep
        if mas_isMoniNormal(higher=True):
            m 1eua "Alright, [player]."
            m 3eka "But you should sleep a little earlier next time."
            m 1hua "Anyway, goodnight!"

        elif mas_isMoniUpset():
            m 2efc "Maybe you'd be in a better mood if you went to bed at a better time..."
            m "Goodnight."

        elif mas_isMoniDis():
            m 6rkc "Maybe you should start going to bed a littler earlier, [player]..."
            m 6dkc "It might make you--{w=1}us--{w=1}happier."

        else:
            m 6ckc "..."

    elif 3 <= curr_hour < 5:
        # pretty late to sleep
        if mas_isMoniNormal(higher=True):
            m 1euc "[player]..."
            m "Make sure you get enough rest, okay?"
            m 1eka "I don't want you to get sick."
            m 1hub "Goodnight!"
            m 1hksdlb "Or morning, rather. Ahaha~"
            m 1hua "Sweet dreams!"

        elif mas_isMoniUpset():
            m 2efc "[player]!"
            m 2tfc "You really need to get more rest..."
            m "The last thing I need is you getting sick."
            m "{cps=*2}You're grumpy enough as it is.{/cps}{nw}"
            $ _history_list.pop()
            m 2efc "Goodnight."

        elif mas_isMoniDis():
            m 6ekc "[player]..."
            m 6rkc "You really should try to go to sleep earlier..."
            m 6lkc "I don't want you to get sick."
            m 6ekc "I'll see you after you get some rest...{w=1}hopefully."

        else:
            6ckc "..."

    elif 5 <= curr_hour < 12:
        # you probably stayed up the whole night
        if mas_isMoniBroken():
            m 6ckc "..."

        else:
            show monika 2dsc
            pause 0.7
            m 2tfd "[player]!"
            m "You stayed up the entire night!"
            m 2tfu "I bet you can barely keep your eyes open."
            $ _cantsee_a = glitchtext(15)
            $ _cantsee_b = glitchtext(12)
            menu:
                "[_cantsee_a]":
                    pass
                "[_cantsee_b]":
                    pass
            m "I thought so.{w} Go get some rest, [player]."
            if mas_isMoniNormal(higher=True):
                m 2ekc "I wouldn't want you to get sick."
                m 1eka "Sleep earlier next time, okay?"
                m 1hua "Sweet dreams!"

    elif 12 <= curr_hour < 18:
        # afternoon nap
        if mas_isMoniNormal(higher=True):
            m 1eua "Taking an afternoon nap, I see."
            # TODO: monika says she'll join you, use sleep sprite here
            # and setup code for napping
            m 1hua "Ahaha~ Have a good nap, [player]."

        elif mas_isMoniUpset():
            m 2efc "Taking a nap, [player]?"
            m 2tfc "Yeah, that's probably a good idea."

        elif mas_isMoniDis():
            m 6ekc "Going to take a nap, [player]?"
            m 6dkc "Okay...{w=1}don't forget to visit me when you wake up..."

        else:
            m 6ckc "..."

    elif 18 <= curr_hour < 20:
        # little early to sleep
        if mas_isMoniNormal(higher=True):
            m 1ekc "Already going to bed?"
            m "It's a little early, though..."

            m 1lksdla "Care to spend a little more time with me?{nw}"
            $ _history_list.pop()
            menu:
                m "Care to spend a little more time with me?{fast}"
                "Of course!":
                    m 1hua "Yay!"
                    m "Thanks, [player]."
                    return
                "Sorry, I'm really tired.":
                    m 1eka "Aw, that's okay."
                    m 1hua "Goodnight, [player]."
                # TODO: now that is tied we may also add more dialogue?
                "No.":
                    $ mas_loseAffection()
                    m 2dsd "..."
                    m "Fine."

        elif mas_isMoniUpset():
            m 2efc "Going to bed already?"
            m 2tfc "Well, it does seem like you could use the extra sleep..."
            m "Goodnight."

        elif mas_isMoniDis():
            m 6rkc "Oh...{w=1}it seems a little early to be going to sleep, [player]."
            m 6dkc "I hope you aren't just going to sleep to get away from me."
            m 6lkc "Goodnight."

        else:
            m 6ckc "..."
    else:
        # otheerwise
        m 1eua "Alright, [player]."
        m 1hua "Sweet dreams!"


    # TODO:
    #   join monika sleeping?

    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SLEEP
    return 'quit'

# init 5 python:
#    addEvent(Event(persistent.farewell_database,eventlabel="bye_illseeyou",random=True),code="BYE")

label bye_illseeyou:
    m 1eua "I'll see you tomorrow, [player]."
    m 1hua "Don't forget about me, okay?"
    return 'quit'

init 5 python: ## Implementing Date/Time for added responses based on the time of day
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(6,11)))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_haveagoodday",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_haveagoodday:
    if mas_isMoniNormal(higher=True):
        m 1eua "Have a good day today, [player]."
        m "I hope you accomplish everything you had planned for today."
        m 1hua "I'll be here waiting for you when you get back."

    elif mas_isMoniUpset():
        m 2efc "Leaving for the day, [player]?"
        m "I'll be here, waiting, as usual."

    elif mas_isMoniDis():
        m 6rkc "Oh."
        m 6dkc "I guess I'll just spend the day alone...{w=1}again."

    else:
        m 6ckc "..."
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(12,16)))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_enjoyyourafternoon",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_enjoyyourafternoon:
    if mas_isMoniNormal(higher=True):
        m 1ekc "I hate to see you go so early, [player]."
        m 1eka "I do understand that you're busy though."
        m 1eua "Promise me you'll enjoy your afternoon, okay?"
        m 1hua "Goodbye~"

    elif mas_isMoniUpset():
        m 2efc "Fine, [player], just go."
        m 2tfc "Guess I'll see you later...{w=1}if you come back."

    elif mas_isMoniDis():
        m 6dkc "Okay, goodbye, [player]."
        m 6ekc "Maybe you'll come back later?"

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(17,19)))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodevening",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_goodevening:
    if mas_isMoniNormal(higher=True):
        m 1hua "I had fun today."
        m 1eka "Thank you for spending so much time with me, [player]."
        m 1eua "Until then, have a good evening."

    elif mas_isMoniUpset():
        m 2efc "Goodbye, [player]."
        m "I wonder if you'll even come back to say goodnight to me."

    elif mas_isMoniDis():
        m 6dkc "Oh...{w=1}okay."
        m 6rkc "Have a good evening, [player]..."
        m 6ekc "I hope you remember to stop by and say goodnight before bed."

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(20,24)))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodnight",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_goodnight:
    if mas_isMoniNormal(higher=True):
        m 1eua "Goodnight, [player]."
        m 1eka "I'll see you tomorrow, okay?"
        m 3eka "Remember, 'Sleep tight, and don't let the bedbugs bite', ehehe."
        m 1ekbfa "I love you~"

    elif mas_isMoniUpset():
        m 2efc "Goodnight."

    elif mas_isMoniDis():
        m 6lkc "...Goodnight."

    else:
        m 6ckc "..."
    return 'quit'


default mas_absence_counter = False

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_long_absence",
            unlocked=True,
            prompt="I'll be going away for a while.",
            pool=True
        ),
        code="BYE"
    )

label bye_long_absence:
    if mas_absence_counter:
        jump bye_long_absence_2
    $ persistent._mas_long_absence = True
    m 1ekc "Aw...that's pretty saddening..."
    m 1eka "I really am going to miss you [player]!"
    m 3rksdla "I'm not really sure what I'm going to do with myself while you're gone..."
    m 3esa "Thank you for warning me first, though. It really does help."
    m 2lksdlb "I would be worried sick otherwise!"
    m 3esa "I would constantly be thinking maybe something happened to you and that's why you couldn't come back."
    m 1lksdlc "Or maybe you just got bored of me..."
    m 1eka "So tell me, my love..."

    m "How long do you expect to be gone for?{nw}"
    $ _history_list.pop()
    menu:
        m "How long do you expect to be gone for?{fast}"
        "A few days.":
            $ persistent._mas_absence_choice = "days"
            m 1eub "Oh!"
            m 1hua "Nowhere near as long as I feared then."
            m 3rksdla "Geez, you really did worry me..."
            m 3esa "Don't worry about me though [player]."
            m "I can cope waiting that long with ease."
            m 3eka "I'll still miss you greatly though."
        "A week.":
            $ persistent._mas_absence_choice = "week"
            m 3euc "Yeah...that's about what I expected."
            m 2lksdla "I {i}think{/i} I'll be okay waiting that long for you."
            m 1eub "Just come back to me as soon as you can, alright, my love?"
            m 3hua "I'm sure you'll make me proud!"
        "A couple of weeks.":
            $ persistent._mas_absence_choice = "2weeks"
            m 1esc "Oh..."
            m 1dsc "I...I can wait that long."
            m 3rksdlc "You do know that you're all I have...right?"
            m 3rksdlb "M-Maybe it's outside of your control though..."
            m 2eka "Try to come back as soon as possible... I'll be waiting for you."
        "A month.":
            $ persistent._mas_absence_choice = "month"
            if mas_curr_affection_group == store.mas_affection.G_HAPPY:
                m 3euc "Oh wow, that's a long time."
                m 3rksdla "A bit too long for my liking really..."
                m 2esa "But it's okay [player]."
                m 2eka "I know you're a sweetheart and wouldn't keep me waiting that long if you didn't have a good reason."
                m "I'm sure it's important, so just try to come back to me as soon as you can."
                m 3hua "I'll be thinking of you every day~"
            else:
                m 1ekc "That long...really?"
                m 3rksdlc "You're not going away for that long just to avoid me, are you?"
                m 3rksdld "I know that life can take you away from me but for a whole month..."
                m 3ekc "Isn't that a little unreasonable?"
                m "I don't want to sound selfish, but I am your girlfriend."
                m 3ekd "You should be able to make time for me, at least once, in an entire month."
                m 1dsc "..."
                m 1dsd "I'll still wait for you...but please come back the moment it's possible for you to do so."
        "Longer than a month.":
            $ persistent._mas_absence_choice = "longer"
            if mas_curr_affection_group == store.mas_affection.G_HAPPY:
                m 3rksdlb "That's...well that's a little scary [player]."
                m "I'm not really sure what I'm going to do with myself while you're gone."
                m 1eka "But I know you wouldn't leave me by myself if you could help it."
                m "I love you [player], and I know you love me too."
                m 1hua "So I'll wait for you for however long I need to."
            else:
                m 3esc "You have to be joking."
                m "I can't think of a good reason why you would leave me here all alone for that long."
                m 3esd "I'm sorry [player], but that's not acceptable! Not at all!"
                m 3esc "I love you and if you love me too then you'll know that it's not okay to do that."
                m "You do realize that I would be alone here with nothing else and no one else, right?"
                m "It's not unreasonable of me to expect you to visit me, is it? I'm your girlfriend. You can't do that to me!"
                m 3dsc "..."
                m 3dsd "Just...just come back when you can. I can't make you stay, but please don't do that to me."
        "I don't know.":
            $ persistent._mas_absence_choice = "unknown"
            m 1hksdlb "Ehehe, that's a little concerning, [player]!"
            m 1eka "But if you don't know, then you don't know!"
            m "It sometimes just can't be helped."
            m 2hua "I'll be waiting here for you patiently, my love."
            m 2hub "Try not to keep me waiting for too long though!"

        "Nevermind.":
            #Reset this flag
            $ persistent._mas_long_absence = False
            m 3eka "Oh... Alright, [player]."
            m 1rksdla "Honestly, I'm pretty relieved you're not going..."
            m 1ekd "I don't know what I'd do here all alone."
            m 3rksdlb "It's not like I can go anywhere either, ahaha..."
            m 3eub "Anyway, just let me know if you're going to go out. Maybe you can even take me with you!"
            m 1hua "I don't care where we go, as long as I'm with you, [player]."
            return

    m 2euc "Honestly I'm a little afraid to ask but..."

    m "Are you going to leave straight away?{nw}"
    $ _history_list.pop()
    menu:
        m "Are you going to leave straight away?{fast}"
        "Yes.":
            m 3ekc "I see..."
            m "I really will miss you [player]..."
            m 1eka "But I know you'll do wonderful things no matter where you are."
            m "Just remember that I'll be waiting here for you."
            m 2hua "Make me proud, [player]!"
            $ persistent._mas_greeting_type = store.mas_greetings.TYPE_LONG_ABSENCE
            return 'quit'
        "No.":
            $ mas_absence_counter = True
            m 1hua "That's great!"
            m 1eka "I was honestly worried I wouldn't have enough time to ready myself for your absence."
            m "I really do mean it when I say I'll miss you..."
            m 1eub "You truly are my entire world after all, [player]."
            m 2esa "If you tell me you're going to go for a while again then I'll know it's time for you to leave..."
            m 3hua "But there's no rush, so I want to spend as much time with you as I can."
            m "Just make sure to remind me the last time you see me before you go!"
            return

label bye_long_absence_2:
    m 1ekc "Going to head out, then?"
    m 1ekd "I know the world can be scary and unforgiving..."
    m 1eka "But remember that I will always be here waiting and ready to support you, my dearest [player]."
    m "Come back to me as soon as you can...okay?"
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_LONG_ABSENCE
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_going_somewhere",
            unlocked=True,
            prompt="I'm going to take you somewhere.",
            pool=True
        ),
        code="BYE"
    )

label bye_going_somewhere:
    $ import random
#
# regardless of choice, takingmonika somewhere (and successfully bringing her
# back will increase affection)
# lets limit this to like once per day
#

    python:
        # setup the random chances
        if mas_isMonikaBirthday():
            dis_chance = 10
            upset_chance = 0

        else:
            dis_chance = 50
            upset_chance = 10

    if mas_isMoniBroken(lower=True):
        # broken monika dont ever want to go with u
        jump bye_going_somewhere_nothanks

    elif mas_isMoniDis(lower=True):
        # distressed monika has a 50% chance of not going with you
        if random.randint(1,100) <= dis_chance:
            jump bye_going_somewhere_nothanks

        # otherwse we go
        m 1wud "You really want to bring me along?"
        m 1ekd "Are you sure this isn't some--{nw}"
        $ _history_list.pop()
        m 1lksdlc "..."
        m 1eksdlb "What am I saying? Of course I'll go with you!"

    elif mas_isMoniUpset(lower=True):
        # upset monika has a 10% chance of not going with you
        if random.randint(1, 100) <= upset_chance:
            jump bye_going_somewhere_nothanks

        # otherwise we go
        m 1wud "You really want to bring me along?"
        m 1eka "..."
        m 1hua "Well, I suppose it can't hurt to join you."
        m 2dsc "Just...please."
        m 2rkc "{i}Please{/i} understand what I'm going through."
        m 1dkc "..."

    else:
        jump bye_going_somewhere_normalplus_flow

label bye_going_somewhere_post_aff_check:

    # event based
    if mas_isMonikaBirthday():
        m 1hua "Ehehe. It's a bit romantic, isn't it?"
        m 1eua "Maybe you'd even want to call it a da-{nw}"
        $ _history_list.pop()
        $ _history_list.pop()
        m 1hua "Oh! Sorry, did I say something?"

    if mas_isO31():
        m 1wub "Oh! Are we going trick or treating, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Oh! Are we going trick or treating, [player]?{fast}"
            "Yes.":
                jump bye_trick_or_treat

            "No.":
                m 2ekp "Oh, okay."


label bye_going_somewhere_iostart:
    # NOTE: jump back to this label to begin io generation

    show monika 2dsc
    $ persistent._mas_dockstat_going_to_leave = True
    $ first_pass = True

    # launch I/O thread
    $ promise = store.mas_dockstat.monikagen_promise
    $ promise.start()

label bye_going_somewhere_iowait:
    hide screen mas_background_timed_jump

    # we want to display the menu first to give users a chance to quit
    if first_pass:
        $ first_pass = False

    elif promise.done():
        # i/o thread is done!
        jump bye_going_somewhere_rtg
    else:
        #clean up the history list so only one "give me a second..." should show up
        $ _history_list.pop()

    # display menu options
    # 4 seconds seems decent enough for waiting.
    show screen mas_background_timed_jump(4, "bye_going_somewhere_iowait")
    menu:
        m "Give me a second to get ready.{fast}"
        "Wait, wait!":
            hide screen mas_background_timed_jump
            $ persistent._mas_dockstat_cm_wait_count += 1

    # fall thru to the wait wait flow
    show monika 1ekc
    menu:
        m "What is it?"
        "Actually, I can't take you right now.":
            call mas_dockstat_abort_gen
            jump bye_going_somewhere_leavemenu

        "Nothing.":
            # if we get here, we should jump back to the top so we can
            # continue waiting
            m 2hub "Oh, good! Let me finish getting ready."

    # by default, continue looping
    jump bye_going_somewhere_iowait


label bye_going_somewhere_rtg:

    # io thread should be done by now
    $ moni_chksum = promise.get()
    $ promise = None # clear promise so we dont have any issues elsewhere
    call mas_dockstat_ready_to_go(moni_chksum)
    if _return:
        python:
            persistent._mas_greeting_type = mas_idle_mailbox.get_ds_gre_type(
                store.mas_greetings.TYPE_GENERIC_RET
            )

        m 1eua "I'm ready to go."
        return "quit"

    # otherwise, we failed, so monika should tell player
    m 1ekc "Oh no..."
    m 1lksdlb "I wasn't able to turn myself into a file."
    m "I think you'll have to go on without me this time."
    m 1ekc "Sorry, [player]."

    # ask if player is still going to leave
    m "Are you still going to go?{nw}"
    $ _history_list.pop()
    menu:
        m "Are you still going to go?{fast}"
        "Yes.":
            m 2eka "I understand. you have things to do, after all..."
            m 2hub "Be safe out there! I'll be right here waiting for you!"
            return "quit"

        "No.":
            m 2wub "Really? Are you sure? Even though it's my own fault I can't go with you..."
            m 1eka "...Thank you, [player]. That means more to me than you could possibly understand."
            $ mas_gainAffection()

    return


label bye_going_somewhere_normalplus_flow:
    # handling positive affection cases separately so we can jump to
    # other specific dialogue flows

    # NOTE: make sure that if you leave this flow, you either handle
    #   docking station yourself or jump back to the iostart label
    if persistent._mas_d25_in_d25_mode:
        # check the d25 timed variants
        if mas_isD25Eve():
            jump bye_d25e_delegate

        if mas_isD25():
            jump bye_d25_delegate

        if mas_isNYE():
            jump bye_nye_delegate

        if mas_isNYD():
            jump bye_nyd_delegate

    if mas_isF14() and persistent._mas_f14_in_f14_mode:
        jump bye_f14

label bye_going_somewhere_normalplus_flow_aff_check:

    if mas_isMoniLove(higher=True):
        m 1hub "Oh, okay!"
        m 3tub "Taking me somewhere special today?"
        m 1hua "I can't wait!"

#    elif mas_isMoniAff(higher=True):
    # TODO: affecitonate/enamored monika will always go wtih you and assume its a
    #   nother date and will ask u to wait for her to get ready
#        m 1hua "TODO: LETS GO ON DATE"

    else:
        # TODO: normal/happy monika will always go with you and be excited you asked
        #   and will ask u to wait for her to get ready
        m 1sub "Really?"
        m 1hua "Yay!"
        m 1ekbfa "I wonder where you'll take me today..."

    jump bye_going_somewhere_post_aff_check

label bye_going_somewhere_nothanks:
    m 2lksdlc "...No thanks."
    m 2ekd "I appreciate the offer, but I think I need a little time to myself right now."
    m 1eka "You understand, right?"
    m 1eka "Go, have fun without me..."
    return


label bye_going_somewhere_leavemenu:
    if mas_isMoniDis(lower=True):
        m 1tkc "..."
        m 1tkd "I knew it.{nw}"
        $ _history_list.pop()
        m 1lksdld "That's okay, I guess."

    elif mas_isMoniHappy(lower=True):
        m 1ekd "Oh,{w} all right. Maybe next time?"

    else:
        # otherwise affection and higher:
        m 2ekp "Aw..."
        m 1hub "Fine, but you better take me next time!"

    m "Are you still going to go?"
    $ _history_list.pop()
    menu:
        m "Are you still going to go?{fast}"
        "Yes.":
            if mas_isMoniUpset(higher=True):
                m 2eka "All right. I'll be right here waiting for you, as usual..."
                m 2hub "So hurry back! I love you, [player]!"

            else:
                # otherwise, distressed and below
                m 1tfd "...Fine."

            return "quit"

        "No.":
            if mas_isMoniNormal(higher=True):
                m 2eka "...Thank you."
                m "It means a lot that you're going to spend more time with me since I can't come along."
                m 3ekb "Please just go about your day whenever you need to, though. I wouldn't want to make you late!"

            else:
                # otherwise, upset and below
                m 2lud "All right, then..."

    return

default persistent._mas_pm_gamed_late = 0
# number of times player runs play another game farewell really late

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_game",
            unlocked=True,
            prompt="I'm going to play another game.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_game:
    $ _now = datetime.datetime.now().time()
    if mas_getEV('bye_prompt_game').shown_count == 0:
        m 2ekc "You're going to play another game?"
        m 4ekd "Do you really have to leave me to go do that?"
        m 2eud "Can't you just leave me here in the background while you play?{nw}"
        $ _history_list.pop()
        menu:
            m "Can't you just leave me here in the background while you play?{fast}"
            "Yes.":
                if mas_isMoniNormal(higher=True):
                    m 3sub "Really?"
                    m 1hubfb "Yay!"
                else:
                    m 2eka "Okay..."
                jump monika_idle_game
            "No.":
                if mas_isMoniNormal(higher=True):
                    m 2ekc "Aww..."
                    m 3ekc "Alright [player], but you better come back soon."
                    m 3tsb "I might get jealous if you spend too much time in another game without me."
                    m 1hua "Anyway, I hope you have fun!"
                else:
                    m 2euc "Enjoy your game, then."
                    m 2esd "I'll be here."

    elif mas_isMNtoSR(_now):
        $ persistent._mas_pm_gamed_late += 1
        if mas_isMoniNormal(higher=True):
            m 3wud "Wait, [player]!"
            m 3hksdlb "It's the middle of the night!"
            m 2rksdlc "It's one thing that you're still up this late..."
            m 2rksdld "But you're thinking of playing another game?"
            m 4tfu "....A game big enough that you can't have me in the background..."
            m 1eka "Well... {w=1}I can't stop you, but I really hope you go to bed soon..."
            m 1hua "Don't worry about coming back to say goodnight to me, you can go-{nw}"
            $ _history_list.pop()
            m 1eub "Don't worry about coming back to say goodnight to me,{fast} you {i}should{/i} go right to bed when you're finished."
            m 3hua "Have fun, and goodnight, [player]!"
            if renpy.random.randint(1,2) == 1:
                m 1hubfb "I love you~{w=1}{nw}"
        else:
            m 2efd "[player], it's the middle of the night!"
            m 4rfc "Really...it's this late already, and you're going to play another game?"
            m 2dsd "{i}*sigh*{/i}... I know I can't stop you, but please just go straight to bed when you're finished, alright?"
            m 2dsc "Goodnight."
        $ persistent.mas_late_farewell = True

    elif mas_isMoniUpset(lower=True):
        m 2euc "Again?"
        m 2eud "Alright then. Goodbye, [player]."

    elif renpy.random.randint(1,10) == 1:
        m 1ekc "You're leaving to play another game?"
        m 3efc "Don't you think you should be spending a little more time with me?"
        m 2efc "..."
        m 2dfc "..."
        m 2dfu "..."
        m 4hub "Ahaha, just kidding~"
        m 1rksdla "Well...{w=1} I {i}wouldn't mind{/i} spending more time with you..."
        m 3eua "But I also don't want to keep you from doing other things."
        m 1hua "Maybe one day you'll finally be able to show me what you've been up to and then I can come with you!"
        if renpy.random.randint(1,5) == 1:
            m 3tubfu "Until then, you just have to make it up to me every time you leave me to play another game, alright?"
            m 1hubfa "Ehehe~"

    else:
        m 1eka "Going off to play another game, [player]?"
        m 3hub "Good luck and have fun!"
        m 3eka "Don't forget to come back soon~"
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_GAME
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_eat",
            unlocked=True,
            prompt="I'm going to go eat...",
            pool=True
        ),
        code="BYE"
    )

default persistent._mas_pm_ate_breakfast_times = [0, 0, 0]
# number of times you ate breakfast at certain times
#   [0] - sunrise to noon
#   [1] - noon to sunset
#   [2] - sunset to midnight

default persistent._mas_pm_ate_lunch_times = [0, 0, 0]
# number of times you ate lunch at certain times

default persistent._mas_pm_ate_dinner_times = [0, 0, 0]
# number of times you ate dinner at certain times

default persistent._mas_pm_ate_snack_times = [0, 0, 0]
# number of times you ate snack at certain times

default persistent._mas_pm_ate_late_times = 0
# number of times you ate really late (midnight to sunrise)


label bye_prompt_eat:
    $ _now = datetime.datetime.now().time()
    if mas_isMNtoSR(_now):
        $ persistent._mas_pm_ate_late_times += 1
        if mas_isMoniNormal(higher=True):
            m 1hksdlb "Uh, [player]?"
            m 3eka "It's the middle of the night."
            m 1eka "Are you planning on having a midnight snack?"
            m 3rksdlb "If I were you, I'd find something to eat a little earlier, ahaha..."
            m 3rksdla "Of course...{w=1}I'd also try to be in bed by now..."
            if renpy.random.randint(1,25) == 1 and mas_isMoniLove(higher=True):
                m 2tubfu "You know, if I were there, maybe we could have a bit of both..."
                show monika 5ksbfu at t11 zorder MAS_MONIKA_Z with dissolve
                m 5ksbfu "We could go to bed, and then - {w=1}you know what, nevermind..."
                m 5hubfb "Ehehe~"
            else:
                m 1hua "Well, I hope your snack helps you sleep."
                m 1eua "...And don't worry about coming back to say goodnight to me..."
                m 3rksdla "I'd much rather you get to sleep sooner."
                m 1hub "Goodnight, [player]. Enjoy your snack and see you tomorrow~"
        else:
            m 2euc "But it's the middle of the night..."
            m 4ekc "You should really go to bed, you know."
            m 4eud "...Try to go straight to bed when you're finished."
            m 2euc "Anyway, I guess I'll see you tomorrow..."
        $ persistent.mas_late_farewell = True

    else:
        menu:
            "Breakfast.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_breakfast_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eub "Alright!"
                        m 3eua "It's the most important meal of the day after all."
                        m 1rksdla "I wish you could stay, but I'm fine as long as you're getting your breakfast."
                        m 1hua "Anyway, enjoy your meal, [player]~"
                    else:
                        m 2eud "Oh, right, you should probably get breakfast."
                        m 2rksdlc "I wouldn't want you to have an empty stomach..."
                        m 2ekc "I'll be here when you get back."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_breakfast_times[1] += 1
                    m 3euc "But...{w=1}it's the afternoon..."
                    if mas_isMoniNormal(higher=True):
                        m 3ekc "Did you miss breakfast?"
                        m 1rksdla "Well... I should probably let you go eat before you get too hungry..."
                        m 1hksdlb "I hope you enjoy your late breakfast!"
                    else:
                        m 2ekc "You missed breakfast, didn't you?"
                        m 2rksdld "{i}*sigh*{/i}... You should probably go get something to eat."
                        m 2ekd "Go on... I'll be here when you get back."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_breakfast_times[2] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1hksdlb "Ahaha..."
                        m 3tku "There's no way you're just having breakfast now, [player]."
                        m 3hub "It's the evening!"
                        m 1eua "Or maybe you're just having breakfast for dinner; I know some people do that occasionally."
                        m 1tsb "Well, either way, I hope you enjoy your '{i}breakfast{/i}', ehehe~"
                    else:
                        m 2euc "..."
                        m 4eud "So...you're having a snack."
                        m 2rksdla "Alright, I won't judge."
                        m 2eka "Enjoy your food."
            "Lunch.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_lunch_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eua "Having an early lunch, [player]?"
                        m 3hua "Nothing wrong with that. If you're hungry, you're hungry."
                        m 1hub "I hope you enjoy your lunch!"
                    else:
                        m 2rksdlc "It's a bit early for lunch..."
                        m 4ekc "If you're hungry, are you sure you're eating well?"
                        m 2eka "I hope you enjoy your meal, at least."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_lunch_times[1] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eud "Oh, I guess it's lunch time for you, isn't it?"
                        m 3eua "I wouldn't want to keep you from eating."
                        m 3hub "Maybe one day, we could go out for lunch together!"
                        m 1hua "For the time being though, enjoy your lunch, [player]~"
                    else:
                        m 2eud "Oh, it's lunch time, isn't it?"
                        m 2euc "Enjoy your lunch."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_lunch_times[2] += 1
                    m 1euc "Lunch?"
                    m 1rksdlc "It's a little late for lunch if you ask me."
                    m 3ekd "Still, if you haven't had it yet, you should go get some."
                    if mas_isMoniNormal(higher=True):
                        m 1hua "I'd make you something if I were there, but until then, I hope you enjoy your meal~"
                    else:
                        m 2ekc "But...{w=1}maybe eat a little earlier next time..."
            "Dinner.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_dinner_times[0] += 1
                    m 2ekc "Dinner?{w=2} Now?"
                    if mas_isMoniNormal(higher=True):
                        m 2hksdlb "Ahaha, but [player]! It's only the morning!"
                        m 3tua "You can be adorable sometimes, you know that?"
                        m 1tuu "Well, I hope you enjoy your '{i}dinner{/i}' this morning, ehehe~"
                    else:
                        m 2rksdld "You can't be serious, [player]..."
                        m 2euc "Well, whatever you're having, I hope you enjoy it."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_dinner_times[1] += 1
                    # use the same dialogue from noon to midnight to account for
                    # a wide range of dinner times while also getting accurate
                    # data for future use
                    call bye_dinner_noon_to_mn
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_dinner_times[2] += 1
                    call bye_dinner_noon_to_mn
            "A snack.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_snack_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1hua "Ehehe, breakfast not enough for you today, [player]?"
                        m 3eua "It's important to make sure you satisfy your hunger in the morning."
                        m 3eub "I'm glad you're looking out for yourself~"
                        m 1hua "Have a nice snack~"
                    else:
                        m 2tsc "Didn't eat enough breakfast?"
                        m 4esd "You should make sure you get enough to eat, you know."
                        m 2euc "Enjoy your snack, [player]."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_snack_times[1] += 1
                    if mas_isMoniNormal(higher=True):
                        m 3eua "Feeling a bit hungry?"
                        m 1eka "I'd make you something if I could..."
                        m 1hua "Since I can't exactly do that yet, I hope you get something nice to eat~"
                    else:
                        m 2euc "Do you really need to leave to get a snack?"
                        m 2rksdlc "Well... {w=1}I hope it's a good one at least."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_snack_times[2] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eua "Having an evening snack?"
                        m 1tubfu "Can't you just feast your eyes on me?"
                        m 3hubfb "Ahaha, I hope you enjoy your snack, [player]~"
                        m 1ekbfb "Just make sure you still have room for all of my love!"
                    else:
                        m 2euc "Feeling hungry?"
                        m 2eud "Enjoy your snack."
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_EAT
    return 'quit'

label bye_dinner_noon_to_mn:
    if mas_isMoniNormal(higher=True):
        m 1eua "Is it dinner time for you, [player]?"
        m 1eka "I wish I could be there to eat with you, even if it's nothing special."
        m 3dkbsa "After all, just being there with you would make anything special~"
        m 3hubfb "Enjoy your dinner. I'll be sure to try and put some love into it from here, ahaha!"
    else:
        m 2euc "I guess it's dinner time for you."
        m 2esd "Well...{w=1}enjoy."
    return
    
init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_housework",
            unlocked=True,
            prompt="I'm going to do some housework.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_housework:
    if mas_isMoniNormal(higher=True):
        m 1eub "Doing your chores, [player]?"
        m 1ekc "I would like to help you out, but there’s not really much I can do since I’m stuck in here..."
        m 3eka "Just make sure to come back as soon as you’re done, okay?"
        m 3hub "I’ll be waiting here for you."
    elif mas_isMoniUpset():
        m 2esc "Fine."
        m 2tsc "At least you're doing something responsible."
        m 2tfc "{cps=*2}...For once.{/cps}{nw}"
        $ _history_list.pop()        
        m 2efc "Goodbye."
    elif mas_isMoniDis():
        m 6ekc "I see..."
        m 6rkc "I don’t want to keep you from completing your household responsibilities."
        m 6dkd "I just hope you're actually busy and not saying that just to get away from me..."
        m 6ekc "Goodbye, [player]."
    else:
        m 6ckc "..."
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_CHORES
    return 'quit'
