from collections import namedtuple
import sys

RailsVolume = namedtuple('RailsVolume', ['p_title', 'p_id', 'title', 'id'])

def map_rails_user_id_to_zulip_user_id(rails_user_id):
	return {
		1:9, 2:9, 3:9, 4:9, # | otto (auto-bot), created by me
		5:  8,  # | m.a
		6: 14, # | r.al
		8: 19, # | m.chr
		9:  11, # | j.cl
		12: 12, # | m.cr
		14: 16, # | t.ro
		15: 10, # | l.ty
		16: 21, # n.to
		13: 20, # | c.pf
		7: 17, # | r.wi
		18: 15, # | d.th
		19: 18, # | j.lo
	}[rails_user_id]

class ChannelMapBuilder(object):
	def __init__(self: any, zulip_channels: list[any]) -> None:
		self._zulip_channels = zulip_channels

	def get_map(self):
		return { rails_volume: self._find_channel(rails_volume) for rails_volume in RAILS_VOLUMES }

	def _find_channel(self, rails_volume):
		return next(filter(lambda z_channel: self._is_match(rails_volume, z_channel), self._zulip_channels))

	def _is_match(self, rails_volume, zulip_channel):
		return rails_volume.p_title.lower() == zulip_channel.stream_name.lower()

RAILS_VOLUMES = [
	# ("p_title","p_id","title","id"):
	RailsVolume("A Mangled Fairy-Tale","52","A Mangled Fairy Tale Story Notes","53"),
	RailsVolume("A Mangled Fairy-Tale","52","A Mangled Fairy Tale","44"),
	RailsVolume("Absinthe","10","Absinthe Story Ideas","60"),
	RailsVolume("Absinthe","10","Absinthe Story Notes","61"),
	RailsVolume("Absinthe","10","Blood Faith","11"),
	RailsVolume("Absinthe","10","Glimpse","19"),
	RailsVolume("Absinthe","10","Malignment","59"),
	RailsVolume("Absinthe","10","Penny Dreadful","101"),
	RailsVolume("Absinthe","10","Reprobate","102"),
	RailsVolume("Absinthe","10","The Quest of St. Andor","18"),
	RailsVolume("Blood Faith","11","Blood Faith I","33"),
	RailsVolume("Blood Faith","11","Blood Faith II","34"),
	RailsVolume("Blood Faith","11","Blood Faith III","35"),
	RailsVolume("Blood Faith","11","Blood Faith IV","36"),
	RailsVolume("Blood Faith","11","Blood Faith IX","41"),
	RailsVolume("Blood Faith","11","Blood Faith V","37"),
	RailsVolume("Blood Faith","11","Blood Faith VI","38"),
	RailsVolume("Blood Faith","11","Blood Faith VII","39"),
	RailsVolume("Blood Faith","11","Blood Faith VIII","40"),
	RailsVolume("Blood Faith","11","Blood Faith X","42"),
	RailsVolume("Blood Faith","11","Blood Faith XI","43"),
	RailsVolume("Blood Faith","11","Blood Faith XII","47"),
	RailsVolume("Blood Faith","11","Blood Faith XIII","81"),
	RailsVolume("Blood Faith","11","Blood Faith XIV","86"),
	RailsVolume("Blood Faith","11","Blood Faith XIX","94"),
	RailsVolume("Blood Faith","11","Blood Faith XV","87"),
	RailsVolume("Blood Faith","11","Blood Faith XVI","88"),
	RailsVolume("Blood Faith","11","Blood Faith XVII","92"),
	RailsVolume("Blood Faith","11","Blood Faith XVIII","93"),
	RailsVolume("Blood Faith","11","dramatis personae","62"),
	RailsVolume("Fae Alchemy","109","Faewearing I","110"),
	RailsVolume("Fae Alchemy","109","Faewearing II","120"),
	RailsVolume("Fae Alchemy","109","Reshaped and Returned part 1, edit 1","137"),
	RailsVolume("Fae Alchemy","109","Reshaped and Returned part 1","136"),
	RailsVolume("Fae Alchemy","109","Reshaped and Returned part 2","138"),
	RailsVolume("Fae Alchemy","109","Reshaped and Returned part 3","139"),
	RailsVolume("Kingdom of Horror","95","KoH IX: Halloween Bulwer-Lytton! 3","97"),
	RailsVolume("Kingdom of Horror","95","KoH IX: Rhymes of the Dead 9","96"),
	RailsVolume("Kingdom of Horror","95","KoH IX: Stories IX","98"),
	RailsVolume("Kingdom of Horror","82","KoH VIII: Flash Fiction Stories","83"),
	RailsVolume("Kingdom of Horror","82","KoH VIII: Halloween Bulwer-Lytton! 2","85"),
	RailsVolume("Kingdom of Horror","82","KoH VIII: Rhymes of the Dead 8","84"),
	RailsVolume("Kingdom of Horror","70","KoH Vol. VII: Chains: Second Link","74"),
	RailsVolume("Kingdom of Horror","70","KoH Vol. VII: Forward","72"),
	RailsVolume("Kingdom of Horror","70","KoH Vol. VII: HALLOWEEN BULWER-LYTTON!","75"),
	RailsVolume("Kingdom of Horror","70","KoH Vol. VII: Poetry","71"),
	RailsVolume("Kingdom of Horror","104","KoH X: Flash Fiction","106"),
	RailsVolume("Kingdom of Horror","104","KoH X: Halloween Bulwer-Lytton! 4","105"),
	RailsVolume("Kingdom of Horror","104","KoH X: Kenny and the Talking Snail","100"),
	RailsVolume("Kingdom of Horror","28","Kingdom of Horror IX","95"),
	RailsVolume("Kingdom of Horror","28","Kingdom of Horror VIII","82"),
	RailsVolume("Kingdom of Horror","28","Kingdom of Horror Vol. VII","70"),
	RailsVolume("Kingdom of Horror","28","Kingdom of Horror X","104"),
	RailsVolume("Kingdom of Horror","28","Tear Drops and Blood Stains3","29"),
	RailsVolume("Kingdom of Horror","28","The Kingdom of Horror 2015","112"),
	RailsVolume("Kingdom of Horror","112","KoH 2015: A Grammatical Horror","115"),
	RailsVolume("Kingdom of Horror","112","KoH 2015: Everything Next Year","114"),
	RailsVolume("Kingdom of Horror","112","KoH 2015: Halloween Bulwer-Lytton! 2015","113"),
	RailsVolume("Krestir","4","Krestir Story Ideas","51"),
	RailsVolume("Krestir","4","Krestir Story Notes","50"),
	RailsVolume("Krestir","4","The Birth of Dragons","7"),
	RailsVolume("Krestir","4","The Creation","5"),
	RailsVolume("Krestir","4","Translation","116"),
	RailsVolume("Christmas Chronicles","45","Ryan's Christmas Stories 2017: Gift of the Mighty","123"),
	RailsVolume("Christmas Chronicles","45","Ryan's Christmas Stories 2017: Santa Gets Hacked","125"),
	RailsVolume("Christmas Chronicles","45","Ryan's Christmas Stories 2017: Yule Cat","124"),
	RailsVolume("Starborn","20","Starborn Story Notes","58"),
	RailsVolume("Starborn","20","Swallowed By Mist","63"),
	RailsVolume("Starborn","20","The Birth of a Legend","57"),
	RailsVolume("Starborn","20","Writ in Stone","56"),
	RailsVolume("The Book Club","9","Running Gags, Jokes, and References in the Sandbox","54"),
	RailsVolume("The Book Club","9","Books Read Prior to January 2011","32"),
	RailsVolume("The Book Club","9","Eva Is Inside Her Cat","66"),
	RailsVolume("The Book Club","9","Gertrude the Governess: or, Simple Seventeen","69"),
	RailsVolume("The Book Club","9","Harvest of Deception","134"),
	RailsVolume("The Book Club","9","Jekyll and Hyde","73"),
	RailsVolume("The Book Club","9","The Game of Rat and Dragon","64"),
	RailsVolume("The Book Club","9","The History of the Book Club","55"),
	RailsVolume("The Book Club","9","The Leather Funnel","80"),
	RailsVolume("The Book Club","9","They Twinkled Like Jewels by Philip José Farmer","67"),
	RailsVolume("Christmas Chronicles","126","A Flapmeier Christmas","78"),
	RailsVolume("Christmas Chronicles","126","A Very Merry Mulitverse","135"),
	RailsVolume("Christmas Chronicles","126","Christmas Bulwer-Lytton","77"),
	RailsVolume("Christmas Chronicles","126","Michael Christenson's GSRs","46"),
	RailsVolume("Christmas Chronicles","126","Ryan's Christmas Stories 2017","45"),
	RailsVolume("Christmas Chronicles","126","Santa's Rough Crowd","132"),
	RailsVolume("Christmas Chronicles","126","Santamorphosis","107"),
	RailsVolume("Christmas Chronicles","126","We Weese You a Merry Christmas","76"),
	RailsVolume("The Coffee Shop","31","ChatGPT about TDaBS","141"),
	RailsVolume("The Coffee Shop","31","DnD","128"),
	RailsVolume("The Coffee Shop","31","EmptyVol","127"),
	RailsVolume("The Coffee Shop","31","Enchanting for Novices","122"),
	RailsVolume("The Coffee Shop","31","Hell Four","111"),
	RailsVolume("The Coffee Shop","31","Il Principe","49"),
	RailsVolume("The Coffee Shop","31","John","108"),
	RailsVolume("The Coffee Shop","31","Major Image Hub","131"),
	RailsVolume("The Coffee Shop","31","Miscellaneous","48"),
	RailsVolume("The Coffee Shop","31","Passed Away","121"),
	RailsVolume("The Coffee Shop","31","Quincy Pough and the Houndworm","142"),
	RailsVolume("The Coffee Shop","31","Rewarded","119"),
	RailsVolume("The Coffee Shop","31","Samantha's Livestream","129"),
	RailsVolume("The Coffee Shop","31","Silent clacked the rosary","65"),
	RailsVolume("The Coffee Shop","31","SOP","103"),
	RailsVolume("The Coffee Shop","31","The Empty Nesters' First Adventure","130"),
	RailsVolume("The Coffee Shop","31","The Monocle","68"),
	RailsVolume("The Coffee Shop","31","The Mortal Ring","118"),
	RailsVolume("The Coffee Shop","31","The Story Must Be Told...Again","140"),
]
