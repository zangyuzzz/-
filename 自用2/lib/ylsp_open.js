import { Crypto, load, _ } from 'assets://js/lib/cat.js';
//import {Axios} from './lib/axios.js';

let key = 'ylsp';
let HOST = 'https://www.iyf.lv';
let parseMap = {};
let siteKey = '';
let siteType = 0;
let cookkie ="";

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';
const UAIPAD = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15 Edg/123.0.0.0';
const UAfirefox ='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0';

async function request(reqUrl) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': UAfirefox,
            //'Referer': HOST
        },
    });
    return res.content;
}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
	//cookkie = await getcook();
    await initParseMap();
}	
async function initParseMap() {
	const date = new Date();
    const t = '' + date.getFullYear() + (date.getMonth() + 1) + date.getDate();
    const js = await request(HOST + '/static/js/playerconfig.js?t=' + t);
    try {
        const jsEval = js + '\nMacPlayerConfig';
        const playerList = eval(jsEval).player_list;
        const players = _.values(playerList);
        _.each(players, (item) => {
            if (!item.ps || item.ps == '0') return;
            if (_.isEmpty(item.parse)) return;
            parseMap[item.show] = item.parse;
        });
    } catch(e) {
    }
}

async function home(filter) {
    const classes = [{'type_id':'1','type_name':'电影'},{'type_id':'2','type_name':'电视剧'},{'type_id':'3','type_name':'综艺'},{'type_id':'4','type_name':'动漫'}];
    const filterObj = {
        '1':[{'key':'cateId','name':'类型','init':'','value':[{'n':'全部','v':'1'},{'n':'动作片','v':'6'},{'n':'喜剧片','v':'7'},{'n':'爱情片','v':'8'},{'n':'科幻片','v':'9'},{'n':'恐怖片','v':'11'},{'n':'剧情片','v':'12'},{'n':'惊悚片','v':'45'},{'n':'奇幻片','v':'10'},{'n':'战争片','v':'20'}]},{'key':'year','name':'年代','init':'','value':[{'n':'全部','v':''},{'n':'2025','v':'2025'},{'n':'2024','v':'2024'},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'}]},{'key': 'area','name': '地区','value': [{'n':'全部','v':''},{'n':'大陆','v':'大陆'},{'n':'香港','v':'香港'},{'n':'台湾','v':'台湾'},{'n':'美国','v':'美国'},{'n':'韩国','v':'韩国'},{'n':'日本','v':'日本'},{'n':'泰国','v':'泰国'},{'n':'新加坡','v':'新加坡'},{'n':'马来西亚','v':'马来西亚'},{'n':'印度','v':'印度'},{'n':'英国','v':'英国'},{'n':'法国','v':'法国'},{'n':'加拿大','v':'加拿大'},{'n':'西班牙','v':'西班牙'},{'n':'俄罗斯','v':'俄罗斯'},{'n':'其它','v':'其它'}]},{'key':'by','name':'排序','init':'','value':[{'n':'添加时间','v':'time_add'},{'n':'更新时间','v':'time_update'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '2':[{'key':'cateId','name':'类型','init':'','value':[{'n':'全部','v':'2'},{'n':'国产剧','v':'13'},{'n':'港台泰','v':'14'},{'n':'日剧','v':'15'},{'n':'欧美剧','v':'16'},{'n':'其他剧','v':'25'}]},{'key':'year','name':'年代','init':'','value':[{'n':'全部','v':''},{'n':'2025','v':'2025'},{'n':'2024','v':'2024'},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'},{'n':'2009','v':'2009'},{'n':'2008','v':'2008'},{'n':'2007','v':'2007'},{'n':'2006','v':'2006'},{'n':'2005','v':'2005'},{'n':'2004','v':'2004'}]},{'key': 'area','name': '地区','value': [{'n':'全部','v':''},{'n':'大陆','v':'大陆'},{'n':'香港','v':'香港'},{'n':'台湾','v':'台湾'},{'n':'美国','v':'美国'},{'n':'韩国','v':'韩国'},{'n':'日本','v':'日本'},{'n':'泰国','v':'泰国'},{'n':'新加坡','v':'新加坡'},{'n':'马来西亚','v':'马来西亚'},{'n':'印度','v':'印度'},{'n':'英国','v':'英国'},{'n':'法国','v':'法国'},{'n':'加拿大','v':'加拿大'},{'n':'西班牙','v':'西班牙'},{'n':'俄罗斯','v':'俄罗斯'},{'n':'其它','v':'其它'}]},{'key':'by','name':'排序','init':'','value':[{'n':'添加时间','v':'time_add'},{'n':'更新时间','v':'time_update'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '3':[{'key':'year','name':'年代','init':'','value':[{'n':'全部','v':''},{'n':'2025','v':'2025'},{'n':'2024','v':'2024'},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'},{'n':'2009','v':'2009'},{'n':'2008','v':'2008'},{'n':'2007','v':'2007'},{'n':'2006','v':'2006'},{'n':'2005','v':'2005'},{'n':'2004','v':'2004'}]},{'key':'by','name':'排序','init':'','value':[{'n':'添加时间','v':'time_add'},{'n':'更新时间','v':'time_update'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '4':[{'key':'year','name':'年代','init':'','value':[{'n':'全部','v':''},{'n':'2025','v':'2025'},{'n':'2024','v':'2024'},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'},{'n':'2009','v':'2009'},{'n':'2008','v':'2008'},{'n':'2007','v':'2007'},{'n':'2006','v':'2006'},{'n':'2005','v':'2005'},{'n':'2004','v':'2004'}]},{'key':'by','name':'排序','init':'','value':[{'n':'添加时间','v':'time_add'},{'n':'更新时间','v':'time_update'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}]
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
	const link = HOST + '/k/' + (extend.cateId || tid) + '-' + (extend.area || '') + '-' + (extend.by) + '--' + (extend.lang || '') + '-'+(extend.letter||'')+'---' + pg + '---' + (extend.year || '') + '.html';//https://91free.live/vodshow/6-%E7%BE%8E%E5%9B%BD-hits--%E8%8B%B1%E8%AF%AD----2---2022.html
    //const html = await request(link);
	//console.debug(link);
    const html = await request(link);
    //console.debug(cookkie);
    //console.debug(html);
    const $ = load(html);
	const items = $('a.module-poster-item.module-item');
    const videos = _.map(items, (item) => {
        const $item = $(item);
        const a = $item;
        const img = $item.find('img:first');
		//console.debug(img.attr('data-original'));
        const remarks = $item.find('div.module-item-note').text().trim();
        return {
            vod_id: a.attr('href').replace(/.*?\/vod\/(.*)\//g, '$1'),
            vod_name: a.attr('title'),
            vod_pic: HOST+img.attr('data-original'),
            vod_remarks: remarks,
        };
    });
    const limit = 72;
    const hasMore = $('div#page > a:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
	
}
async function detail(id) {
	 const html = await request(HOST  + id + '.html');
	//console.debug(id);
	//console.debug(html);
    const $ = load(html);
    const vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim(),
        vod_type: $('.module-info-tag a:eq(2)').text().trim(),
        vod_year: $('.module-info-tag a:eq(0)').text().trim(),
        vod_area: $('.module-info-tag a:eq(1)').text().trim(),
        vod_actor: $('.module-info-item:contains(主演：)').text().trim().substring(3).replace(/\/$/, ''),
        vod_director: $('.module-info-item:contains(导演：)').text().trim().substring(3).replace(/\/$/, ''),
        vod_pic: $('.module-info-poster img:first').attr('data-original'),
        vod_remarks : $('.module-info-item:contains(更新：)').next().text(),
        vod_content: $('.module-info-introduction-content').text().trim(),
    };
    const playMap = {};
    const tabs = $('.module-tab-item.tab-item span');
    const playlists = $('.module-play-list');
    _.each(tabs, (tab, i) => {
        const $tab = $(tab);
        const from = $tab.text().trim();
        let list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            const $it = $(it);
            let title = $it.find('span').text();
            const playUrl = $it.attr('href');
            if (_.isEmpty(title)) title = $it.text();
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push(title + '$' + playUrl);
        });
    });
    vod.vod_play_from = _.keys(playMap).join('$$$');
    const urls = _.values(playMap);
    const vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
	
	
	
	
	
	
	
	
	}

async function play(flag, id, flags) {
	const link = HOST + id;
    const html = await request(link);
	//console.debug(html);
    const $ = load(html);
    const js = JSON.parse($('script:contains(player_aaaa)').html().replace('var player_aaaa=',''));
    let playUrl = js.url;
	//console.debug(playUrl);
	return JSON.stringify({
        parse: 0,
        url: playUrl,
        header: {
            'User-Agent': UA,
        }
    });
	
	
	}

async function search(wd, quick) {
	const html=await request(HOST+'/vodsearch/'+wd+'-------------.html');
	//console.debug(html);
	//const data = JSON.parse(await request(HOST + '/vodsearch/' + wd+'-------------.html')).list;
	
	//console.debug(data);
	const $ = load(html);
    const items = $('.module-card-item.module-item');
	//console.debug(items);
    const videos = _.map(items, (item) => {
        const $item = $(item);
        const a = $item;
        const img = $item.find('img:first');
        const remarks = $item.find('div.module-item-note').text().trim();
		//console.debug(a.find('.module-card-item-poster').attr('href'));
        return {
            vod_id: a.find('.module-card-item-poster').attr('href').replace(/.*?\/vod\/(.*).html/g, '$1'),
            vod_name: img.attr('alt'),
            vod_pic: img.attr('data-original'),
            vod_remarks: remarks,
        };
    });
    return JSON.stringify({
        list: videos,
    });
	
	}
export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}
