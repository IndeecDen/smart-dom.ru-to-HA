/* mdr-intercom-call-card — собранный бандл. Источник: frontend/src/. Не редактировать вручную. */
var lt=Object.defineProperty;var dt=Object.getOwnPropertyDescriptor;var d=(s,t,e,r)=>{for(var i=r>1?void 0:r?dt(t,e):t,n=s.length-1,a;n>=0;n--)(a=s[n])&&(i=(r?a(t,e,i):a(i))||i);return r&&i&&lt(t,e,i),i};var J=globalThis,Z=J.ShadowRoot&&(J.ShadyCSS===void 0||J.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,de=Symbol(),Se=new WeakMap,j=class{constructor(t,e,r){if(this._$cssResult$=!0,r!==de)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(Z&&t===void 0){let r=e!==void 0&&e.length===1;r&&(t=Se.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),r&&Se.set(e,t))}return t}toString(){return this.cssText}},Ae=s=>new j(typeof s=="string"?s:s+"",void 0,de),w=(s,...t)=>{let e=s.length===1?s[0]:t.reduce((r,i,n)=>r+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+s[n+1],s[0]);return new j(e,s,de)},Ee=(s,t)=>{if(Z)s.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let r=document.createElement("style"),i=J.litNonce;i!==void 0&&r.setAttribute("nonce",i),r.textContent=e.cssText,s.appendChild(r)}},pe=Z?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let r of t.cssRules)e+=r.cssText;return Ae(e)})(s):s;var{is:pt,defineProperty:ht,getOwnPropertyDescriptor:ut,getOwnPropertyNames:mt,getOwnPropertySymbols:ft,getPrototypeOf:gt}=Object,Q=globalThis,Re=Q.trustedTypes,vt=Re?Re.emptyScript:"",_t=Q.reactiveElementPolyfillSupport,I=(s,t)=>s,q={toAttribute(s,t){switch(t){case Boolean:s=s?vt:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},ee=(s,t)=>!pt(s,t),Te={attribute:!0,type:String,converter:q,reflect:!1,useDefault:!1,hasChanged:ee};Symbol.metadata??=Symbol("metadata"),Q.litPropertyMetadata??=new WeakMap;var R=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=Te){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let r=Symbol(),i=this.getPropertyDescriptor(t,r,e);i!==void 0&&ht(this.prototype,t,i)}}static getPropertyDescriptor(t,e,r){let{get:i,set:n}=ut(this.prototype,t)??{get(){return this[e]},set(a){this[e]=a}};return{get:i,set(a){let l=i?.call(this);n?.call(this,a),this.requestUpdate(t,l,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Te}static _$Ei(){if(this.hasOwnProperty(I("elementProperties")))return;let t=gt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(I("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(I("properties"))){let e=this.properties,r=[...mt(e),...ft(e)];for(let i of r)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[r,i]of e)this.elementProperties.set(r,i)}this._$Eh=new Map;for(let[e,r]of this.elementProperties){let i=this._$Eu(e,r);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let r=new Set(t.flat(1/0).reverse());for(let i of r)e.unshift(pe(i))}else t!==void 0&&e.push(pe(t));return e}static _$Eu(t,e){let r=e.attribute;return r===!1?void 0:typeof r=="string"?r:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let r of e.keys())this.hasOwnProperty(r)&&(t.set(r,this[r]),delete this[r]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ee(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,r){this._$AK(t,r)}_$ET(t,e){let r=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,r);if(i!==void 0&&r.reflect===!0){let n=(r.converter?.toAttribute!==void 0?r.converter:q).toAttribute(e,r.type);this._$Em=t,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(t,e){let r=this.constructor,i=r._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let n=r.getPropertyOptions(i),a=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:q;this._$Em=i;let l=a.fromAttribute(e,n.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(t,e,r,i=!1,n){if(t!==void 0){let a=this.constructor;if(i===!1&&(n=this[t]),r??=a.getPropertyOptions(t),!((r.hasChanged??ee)(n,e)||r.useDefault&&r.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(a._$Eu(t,r))))return;this.C(t,e,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:r,reflect:i,wrapped:n},a){r&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),n!==!0||a!==void 0)||(this._$AL.has(t)||(this.hasUpdated||r||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let r=this.constructor.elementProperties;if(r.size>0)for(let[i,n]of r){let{wrapped:a}=n,l=this[i];a!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,n,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(e)):this._$EM()}catch(r){throw t=!1,this._$EM(),r}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};R.elementStyles=[],R.shadowRootOptions={mode:"open"},R[I("elementProperties")]=new Map,R[I("finalized")]=new Map,_t?.({ReactiveElement:R}),(Q.reactiveElementVersions??=[]).push("2.1.2");var _e=globalThis,Pe=s=>s,te=_e.trustedTypes,Ce=te?te.createPolicy("lit-html",{createHTML:s=>s}):void 0,De="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,Ne="?"+C,yt=`<${Ne}>`,O=document,W=()=>O.createComment(""),F=s=>s===null||typeof s!="object"&&typeof s!="function",ye=Array.isArray,bt=s=>ye(s)||typeof s?.[Symbol.iterator]=="function",he=`[ 	
\f\r]`,V=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Me=/-->/g,He=/>/g,H=RegExp(`>|${he}(?:([^\\s"'>=/]+)(${he}*=${he}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Le=/'/g,Oe=/"/g,ze=/^(?:script|style|textarea|title)$/i,be=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),c=be(1),Gt=be(2),Yt=be(3),T=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),Ue=new WeakMap,L=O.createTreeWalker(O,129);function Be(s,t){if(!ye(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ce!==void 0?Ce.createHTML(t):t}var xt=(s,t)=>{let e=s.length-1,r=[],i,n=t===2?"<svg>":t===3?"<math>":"",a=V;for(let l=0;l<e;l++){let o=s[l],h,g,u=-1,v=0;for(;v<o.length&&(a.lastIndex=v,g=a.exec(o),g!==null);)v=a.lastIndex,a===V?g[1]==="!--"?a=Me:g[1]!==void 0?a=He:g[2]!==void 0?(ze.test(g[2])&&(i=RegExp("</"+g[2],"g")),a=H):g[3]!==void 0&&(a=H):a===H?g[0]===">"?(a=i??V,u=-1):g[1]===void 0?u=-2:(u=a.lastIndex-g[2].length,h=g[1],a=g[3]===void 0?H:g[3]==='"'?Oe:Le):a===Oe||a===Le?a=H:a===Me||a===He?a=V:(a=H,i=void 0);let y=a===H&&s[l+1].startsWith("/>")?" ":"";n+=a===V?o+yt:u>=0?(r.push(h),o.slice(0,u)+De+o.slice(u)+C+y):o+C+(u===-2?l:y)}return[Be(s,n+(s[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),r]},K=class s{constructor({strings:t,_$litType$:e},r){let i;this.parts=[];let n=0,a=0,l=t.length-1,o=this.parts,[h,g]=xt(t,e);if(this.el=s.createElement(h,r),L.currentNode=this.el.content,e===2||e===3){let u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(i=L.nextNode())!==null&&o.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let u of i.getAttributeNames())if(u.endsWith(De)){let v=g[a++],y=i.getAttribute(u).split(C),P=/([.?@])?(.*)/.exec(v);o.push({type:1,index:n,name:P[2],strings:y,ctor:P[1]==="."?me:P[1]==="?"?fe:P[1]==="@"?ge:N}),i.removeAttribute(u)}else u.startsWith(C)&&(o.push({type:6,index:n}),i.removeAttribute(u));if(ze.test(i.tagName)){let u=i.textContent.split(C),v=u.length-1;if(v>0){i.textContent=te?te.emptyScript:"";for(let y=0;y<v;y++)i.append(u[y],W()),L.nextNode(),o.push({type:2,index:++n});i.append(u[v],W())}}}else if(i.nodeType===8)if(i.data===Ne)o.push({type:2,index:n});else{let u=-1;for(;(u=i.data.indexOf(C,u+1))!==-1;)o.push({type:7,index:n}),u+=C.length-1}n++}}static createElement(t,e){let r=O.createElement("template");return r.innerHTML=t,r}};function D(s,t,e=s,r){if(t===T)return t;let i=r!==void 0?e._$Co?.[r]:e._$Cl,n=F(t)?void 0:t._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(s),i._$AT(s,e,r)),r!==void 0?(e._$Co??=[])[r]=i:e._$Cl=i),i!==void 0&&(t=D(s,i._$AS(s,t.values),i,r)),t}var ue=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:r}=this._$AD,i=(t?.creationScope??O).importNode(e,!0);L.currentNode=i;let n=L.nextNode(),a=0,l=0,o=r[0];for(;o!==void 0;){if(a===o.index){let h;o.type===2?h=new G(n,n.nextSibling,this,t):o.type===1?h=new o.ctor(n,o.name,o.strings,this,t):o.type===6&&(h=new ve(n,this,t)),this._$AV.push(h),o=r[++l]}a!==o?.index&&(n=L.nextNode(),a++)}return L.currentNode=O,i}p(t){let e=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(t,r,e),e+=r.strings.length-2):r._$AI(t[e])),e++}},G=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,r,i){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=r,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=D(this,t,e),F(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==T&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):bt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&F(this._$AH)?this._$AA.nextSibling.data=t:this.T(O.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:r}=t,i=typeof r=="number"?this._$AC(t):(r.el===void 0&&(r.el=K.createElement(Be(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===i)this._$AH.p(e);else{let n=new ue(i,this),a=n.u(this.options);n.p(e),this.T(a),this._$AH=n}}_$AC(t){let e=Ue.get(t.strings);return e===void 0&&Ue.set(t.strings,e=new K(t)),e}k(t){ye(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,r,i=0;for(let n of t)i===e.length?e.push(r=new s(this.O(W()),this.O(W()),this,this.options)):r=e[i],r._$AI(n),i++;i<e.length&&(this._$AR(r&&r._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let r=Pe(t).nextSibling;Pe(t).remove(),t=r}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},N=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,r,i,n){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=p}_$AI(t,e=this,r,i){let n=this.strings,a=!1;if(n===void 0)t=D(this,t,e,0),a=!F(t)||t!==this._$AH&&t!==T,a&&(this._$AH=t);else{let l=t,o,h;for(t=n[0],o=0;o<n.length-1;o++)h=D(this,l[r+o],e,o),h===T&&(h=this._$AH[o]),a||=!F(h)||h!==this._$AH[o],h===p?t=p:t!==p&&(t+=(h??"")+n[o+1]),this._$AH[o]=h}a&&!i&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},me=class extends N{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},fe=class extends N{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},ge=class extends N{constructor(t,e,r,i,n){super(t,e,r,i,n),this.type=5}_$AI(t,e=this){if((t=D(this,t,e,0)??p)===T)return;let r=this._$AH,i=t===p&&r!==p||t.capture!==r.capture||t.once!==r.once||t.passive!==r.passive,n=t!==p&&(r===p||i);i&&this.element.removeEventListener(this.name,this,r),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},ve=class{constructor(t,e,r){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(t){D(this,t)}};var wt=_e.litHtmlPolyfillSupport;wt?.(K,G),(_e.litHtmlVersions??=[]).push("3.3.3");var je=(s,t,e)=>{let r=e?.renderBefore??t,i=r._$litPart$;if(i===void 0){let n=e?.renderBefore??null;r._$litPart$=i=new G(t.insertBefore(W(),n),n,void 0,e??{})}return i._$AI(s),i};var xe=globalThis,b=class extends R{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=je(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return T}};b._$litElement$=!0,b.finalized=!0,xe.litElementHydrateSupport?.({LitElement:b});var $t=xe.litElementPolyfillSupport;$t?.({LitElement:b});(xe.litElementVersions??=[]).push("4.2.2");var k=s=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(s,t)}):customElements.define(s,t)};var kt={attribute:!0,type:String,converter:q,reflect:!1,hasChanged:ee},St=(s=kt,t,e)=>{let{kind:r,metadata:i}=e,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),r==="setter"&&((s=Object.create(s)).wrapped=!0),n.set(e.name,s),r==="accessor"){let{name:a}=e;return{set(l){let o=t.get.call(this);t.set.call(this,l),this.requestUpdate(a,o,s,!0,l)},init(l){return l!==void 0&&this.C(a,void 0,s,l),l}}}if(r==="setter"){let{name:a}=e;return function(l){let o=this[a];t.call(this,l),this.requestUpdate(a,o,s,!0,l)}}throw Error("Unsupported decorator location: "+r)};function m(s){return(t,e)=>typeof e=="object"?St(s,t,e):((r,i,n)=>{let a=i.hasOwnProperty(n);return i.constructor.createProperty(n,r),a?Object.getOwnPropertyDescriptor(i,n):void 0})(s,t,e)}function f(s){return m({...s,state:!0,attribute:!1})}var Ie={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},se=s=>(...t)=>({_$litDirective$:s,values:t}),ie=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,r){this._$Ct=t,this._$AM=e,this._$Ci=r}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var U=class extends ie{constructor(t){if(super(t),this.it=p,t.type!==Ie.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===p||t==null)return this._t=void 0,this.it=t;if(t===T)return t;if(typeof t!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;let e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};U.directiveName="unsafeHTML",U.resultType=1;var Nr=se(U);var Y=class extends U{};Y.directiveName="unsafeSVG",Y.resultType=2;var qe=se(Y);var At={"key-round":'<path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/>',lock:'<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',"lock-open":'<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>',phone:'<path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384"/>',"phone-off":'<path d="M10.1 13.9a14 14 0 0 0 3.732 2.668 1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2 18 18 0 0 1-12.728-5.272"/><path d="M22 2 2 22"/><path d="M4.76 13.582A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 .244.473"/>',mic:'<path d="M12 19v3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><rect x="9" y="2" width="6" height="13" rx="3"/>',"mic-off":'<path d="M12 19v3"/><path d="M15 9.34V5a3 3 0 0 0-5.68-1.33"/><path d="M16.95 16.95A7 7 0 0 1 5 12v-2"/><path d="M18.89 13.23A7 7 0 0 0 19 12v-2"/><path d="m2 2 20 20"/><path d="M9 9v3a3 3 0 0 0 5.12 2.12"/>',"volume-2":'<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"/><path d="M16 9a5 5 0 0 1 0 6"/><path d="M19.364 18.364a9 9 0 0 0 0-12.728"/>',"volume-x":'<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"/><line x1="22" x2="16" y1="9" y2="15"/><line x1="16" x2="22" y1="9" y2="15"/>',x:'<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',timer:'<line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/>',"refresh-cw":'<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',"door-open":'<path d="M11 20H2"/><path d="M11 4.562v16.157a1 1 0 0 0 1.242.97L19 20V5.562a2 2 0 0 0-1.515-1.94l-4-1A2 2 0 0 0 11 4.561z"/><path d="M11 4H8a2 2 0 0 0-2 2v14"/><path d="M14 12h.01"/><path d="M22 20h-3"/>',"video-off":'<path d="M10.66 6H14a2 2 0 0 1 2 2v2.5l5.248-3.062A.5.5 0 0 1 22 7.87v8.196"/><path d="M16 16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h2"/><path d="m2 2 20 20"/>',"wifi-off":'<path d="M12 20h.01"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/><path d="M5 12.859a10 10 0 0 1 5.17-2.69"/><path d="M19 12.859a10 10 0 0 0-2.007-1.523"/><path d="M2 8.82a15 15 0 0 1 4.177-2.643"/><path d="M22 8.82a15 15 0 0 0-11.288-3.764"/><path d="m2 2 20 20"/>',"circle-check":'<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',"chevron-right":'<path d="m9 18 6-6-6-6"/>',"bell-ring":'<path d="M10.268 21a2 2 0 0 0 3.464 0"/><path d="M22 8c0-2.3-.8-4.3-2-6"/><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/><path d="M4 2C2.8 3.7 2 5.7 2 8"/>',"loader-circle":'<path d="M21 12a9 9 0 1 1-6.219-8.56"/>',"door-closed":'<path d="M10 12h.01"/><path d="M18 20V6a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v14"/><path d="M2 20h20"/>'},z=class extends b{constructor(){super(...arguments);this.name=""}render(){let e=At[this.name]??"";return c`<svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >${qe(e)}</svg>`}};z.styles=w`
    :host {
      display: inline-flex;
      width: var(--mdr-icon-size, 24px);
      height: var(--mdr-icon-size, 24px);
      line-height: 0;
      flex: none;
    }
    svg {
      width: 100%;
      height: 100%;
      display: block;
    }
  `,d([m()],z.prototype,"name",2),z=d([k("mdr-icon")],z);function ne(s){return(s?.locale?.language??s?.language??"").toLowerCase().startsWith("en")?"en":"ru"}var Ve={status:{ringing:"\u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0439 \u0432\u044B\u0437\u043E\u0432",connecting:"\u0421\u043E\u0435\u0434\u0438\u043D\u0435\u043D\u0438\u0435\u2026",active:"\u0420\u0430\u0437\u0433\u043E\u0432\u043E\u0440",ended:"\u0412\u044B\u0437\u043E\u0432 \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043D",error:"\u041E\u0448\u0438\u0431\u043A\u0430 \u0432\u044B\u0437\u043E\u0432\u0430"},compact:{call:"\u0412\u044B\u0437\u043E\u0432",talk:"\u0420\u0430\u0437\u0433\u043E\u0432\u043E\u0440",connecting:"\u0421\u043E\u0435\u0434\u0438\u043D\u0435\u043D\u0438\u0435\u2026",ended:"\u0417\u0430\u0432\u0435\u0440\u0448\u0451\u043D",error:"\u041E\u0448\u0438\u0431\u043A\u0430 \u0432\u044B\u0437\u043E\u0432\u0430"},nameFallback:"\u0414\u043E\u043C\u043E\u0444\u043E\u043D",minimize:"\u0421\u0432\u0435\u0440\u043D\u0443\u0442\u044C",idle:{title:"\u041D\u0435\u0442 \u0430\u043A\u0442\u0438\u0432\u043D\u043E\u0433\u043E \u0432\u044B\u0437\u043E\u0432\u0430",sub:"\u0412\u0438\u0434\u0435\u043E \u043F\u043E\u044F\u0432\u0438\u0442\u0441\u044F \u043F\u0440\u0438 \u0437\u0432\u043E\u043D\u043A\u0435 \u0432 \u0434\u043E\u043C\u043E\u0444\u043E\u043D"},action:{accept:"\u041F\u0440\u0438\u043D\u044F\u0442\u044C",reject:"\u041E\u0442\u043A\u043B\u043E\u043D\u0438\u0442\u044C",cancel:"\u041E\u0442\u043C\u0435\u043D\u0438\u0442\u044C",connecting:"\u0421\u043E\u0435\u0434\u0438\u043D\u044F\u0435\u043C\u2026",hangup:"\u0417\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C",retry:"\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C",close:"\u0417\u0430\u043A\u0440\u044B\u0442\u044C",sound:"\u0417\u0432\u0443\u043A",soundOff:"\u0417\u0432\u0443\u043A \u0432\u044B\u043A\u043B.",mic:"\u041C\u0438\u043A\u0440\u043E\u0444\u043E\u043D",micNoAccess:"\u041D\u0435\u0442 \u0434\u043E\u0441\u0442\u0443\u043F\u0430",micOn:"\u0412\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D",micOff:"\u0412\u044B\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D"},micBanner:{no_https:{title:"\u041C\u0438\u043A\u0440\u043E\u0444\u043E\u043D \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D",sub:"\u041E\u0442\u043A\u0440\u043E\u0439\u0442\u0435 Home Assistant \u043F\u043E HTTPS, \u0447\u0442\u043E\u0431\u044B \u0433\u043E\u0432\u043E\u0440\u0438\u0442\u044C \u0432 \u0434\u043E\u043C\u043E\u0444\u043E\u043D."},denied:{title:"\u0414\u043E\u0441\u0442\u0443\u043F \u043A \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D\u0443 \u0437\u0430\u043F\u0440\u0435\u0449\u0451\u043D",sub:"\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u0435 \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D \u0434\u043B\u044F \u044D\u0442\u043E\u0433\u043E \u0441\u0430\u0439\u0442\u0430 \u0432 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0430\u0445 \u0431\u0440\u0430\u0443\u0437\u0435\u0440\u0430.",cta:"\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C"},prompt:{title:"\u041D\u0443\u0436\u0435\u043D \u0434\u043E\u0441\u0442\u0443\u043F \u043A \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D\u0443",sub:"\u041D\u0430\u0436\u043C\u0438\u0442\u0435 \xAB\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C\xBB, \u0447\u0442\u043E\u0431\u044B \u0432\u0430\u0441 \u0431\u044B\u043B\u043E \u0441\u043B\u044B\u0448\u043D\u043E.",cta:"\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044C"}},stage:{cameraOff:{title:"\u0412\u0438\u0434\u0435\u043E \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u043D\u043E",sub:"\u0410\u0443\u0434\u0438\u043E\u0432\u044B\u0437\u043E\u0432 \u043F\u0440\u043E\u0434\u043E\u043B\u0436\u0430\u0435\u0442\u0441\u044F"},connectionLost:{title:"\u0421\u043E\u0435\u0434\u0438\u043D\u0435\u043D\u0438\u0435 \u043F\u0440\u0435\u0440\u0432\u0430\u043D\u043E",sub:"\u041F\u0440\u043E\u0431\u0443\u0435\u043C \u0432\u043E\u0441\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u044C\u2026"},soundOffChip:"\u0417\u0432\u0443\u043A \u0432\u044B\u043A\u043B.",unmuteAria:"\u0412\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0437\u0432\u0443\u043A",unmuteCta:"\u041D\u0430\u0436\u043C\u0438\u0442\u0435, \u0447\u0442\u043E\u0431\u044B \u0432\u043A\u043B\u044E\u0447\u0438\u0442\u044C \u0437\u0432\u0443\u043A"},video:{noVideo:"\u041D\u0435\u0442 \u0430\u043A\u0442\u0438\u0432\u043D\u043E\u0433\u043E \u0432\u0438\u0434\u0435\u043E",cameraUnavailable:"\u041A\u0430\u043C\u0435\u0440\u0430 \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u043D\u0430",loading:"\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u0432\u0438\u0434\u0435\u043E\u2026",playerUnavailable:"\u0412\u0438\u0434\u0435\u043E\u043F\u043B\u0435\u0435\u0440 \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D \u2014 \u043E\u0431\u043D\u043E\u0432\u0438\u0442\u0435 HA \u0438\u043B\u0438 \u0443\u0441\u0442\u0430\u043D\u043E\u0432\u0438\u0442\u0435 advanced-camera-card"},open:{labelDefault:"\u041E\u0442\u043A\u0440\u044B\u0442\u044C \u0434\u0432\u0435\u0440\u044C",opened:"\u041E\u0442\u043A\u0440\u044B\u0442\u043E",opening:"\u041E\u0442\u043A\u0440\u044B\u0432\u0430\u044E\u2026",slide:"\u041E\u0442\u043A\u0440\u044B\u0442\u044C",hold:"\u0423\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0439\u0442\u0435, \u0447\u0442\u043E\u0431\u044B \u043E\u0442\u043A\u0440\u044B\u0442\u044C",captionOpened:"\u0414\u0432\u0435\u0440\u044C \u043E\u0442\u043A\u0440\u044B\u0442\u0430",captionError:"\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u043E\u0442\u043A\u0440\u044B\u0442\u044C \xB7 \u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C",captionSlideHint:"\u0421\u0434\u0432\u0438\u043D\u044C\u0442\u0435, \u0447\u0442\u043E\u0431\u044B \u043E\u0442\u043A\u0440\u044B\u0442\u044C \u0434\u0432\u0435\u0440\u044C",holdAriaSuffix:"\u2014 \u0443\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0439\u0442\u0435"}},Et={status:{ringing:"Incoming call",connecting:"Connecting\u2026",active:"In call",ended:"Call ended",error:"Call error"},compact:{call:"Call",talk:"In call",connecting:"Connecting\u2026",ended:"Ended",error:"Call error"},nameFallback:"Intercom",minimize:"Minimize",idle:{title:"No active call",sub:"Video appears when someone calls"},action:{accept:"Answer",reject:"Decline",cancel:"Cancel",connecting:"Connecting\u2026",hangup:"Hang up",retry:"Retry",close:"Close",sound:"Sound",soundOff:"Sound off",mic:"Mic",micNoAccess:"No access",micOn:"Turn microphone on",micOff:"Turn microphone off"},micBanner:{no_https:{title:"Microphone unavailable",sub:"Open Home Assistant over HTTPS to talk to the intercom."},denied:{title:"Microphone blocked",sub:"Allow the microphone for this site in your browser settings.",cta:"Retry"},prompt:{title:"Microphone access needed",sub:"Tap \u201CAllow\u201D so you can be heard.",cta:"Allow"}},stage:{cameraOff:{title:"Video unavailable",sub:"Audio call continues"},connectionLost:{title:"Connection lost",sub:"Trying to reconnect\u2026"},soundOffChip:"Sound off",unmuteAria:"Turn sound on",unmuteCta:"Tap to turn on sound"},video:{noVideo:"No active video",cameraUnavailable:"Camera unavailable",loading:"Loading video\u2026",playerUnavailable:"Video player unavailable \u2014 update HA or install advanced-camera-card"},open:{labelDefault:"Open door",opened:"Opened",opening:"Opening\u2026",slide:"Open",hold:"Hold to open",captionOpened:"Door opened",captionError:"Couldn\u2019t open \xB7 Retry",captionSlideHint:"Slide to open the door",holdAriaSuffix:"\u2014 hold"}},Rt={ru:Ve,en:Et};function _(s){return Rt[s]??Ve}var Tt={ru:{title:"\u0421\u043E\u0431\u044B\u0442\u0438\u044F",event:{call_accepted:"\u0414\u043E\u043C\u043E\u0444\u043E\u043D: \u043F\u0440\u0438\u043D\u044F\u0442 \u0437\u0432\u043E\u043D\u043E\u043A",call_missed:"\u0414\u043E\u043C\u043E\u0444\u043E\u043D: \u043F\u0440\u043E\u043F\u0443\u0449\u0435\u043D \u0437\u0432\u043E\u043D\u043E\u043A",key_activated:"\u0414\u043E\u043C\u043E\u0444\u043E\u043D: \u043E\u0442\u043A\u0440\u044B\u0442 \u043A\u043B\u044E\u0447\u043E\u043C"},empty:"\u0421\u043E\u0431\u044B\u0442\u0438\u0439 \u043F\u043E\u043A\u0430 \u043D\u0435\u0442",unavailable:"\u041D\u0435 \u0443\u0434\u0430\u043B\u043E\u0441\u044C \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044C \u0438\u0441\u0442\u043E\u0440\u0438\u044E",retry:"\u041F\u043E\u0432\u0442\u043E\u0440\u0438\u0442\u044C",refresh:"\u041E\u0431\u043D\u043E\u0432\u0438\u0442\u044C",more:"\u041F\u043E\u043A\u0430\u0437\u0430\u0442\u044C \u0435\u0449\u0451",loading:"\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u0438\u0441\u0442\u043E\u0440\u0438\u0438\u2026",devices:"\u0423\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430",allDevices:"\u0412\u0441\u0435 \u0443\u0441\u0442\u0440\u043E\u0439\u0441\u0442\u0432\u0430"},en:{title:"Events",event:{call_accepted:"Intercom: answered call",call_missed:"Intercom: missed call",key_activated:"Intercom: opened with a key"},empty:"No events yet",unavailable:"Unable to load history",retry:"Retry",refresh:"Refresh",more:"Show more",loading:"Loading history\u2026",devices:"Devices",allDevices:"All devices"}};function we(s){return typeof s=="object"&&s!==null&&!Array.isArray(s)}function Pt(s){return s==="call_accepted"||s==="call_missed"||s==="key_activated"}function Ct(s){let t=we(s)?s:{},e=typeof t.entity_id=="string"?t.entity_id:"",r=typeof t.source_name=="string"?t.source_name:"",n=(Array.isArray(t.events)?t.events:[]).flatMap(a=>{if(!we(a)||typeof a.event_id!="string"||a.event_id.length===0||!Pt(a.event_type)||typeof a.occurred_at!="number"||!Number.isFinite(a.occurred_at)||!Number.isFinite(new Date(a.occurred_at*1e3).getTime()))return[];let l=typeof a.place_id=="string"?a.place_id:"",o=typeof a.source_id=="string"?a.source_id:"",h=typeof a.source_name=="string"&&a.source_name?a.source_name:r;return[{event_id:a.event_id,event_type:a.event_type,occurred_at:a.occurred_at,feed_id:e,feed_name:r,source_key:l?`${e}:${l}:${o}`:e,source_name:h,...a.event_type==="key_activated"&&typeof a.key_name=="string"?{key_name:a.key_name}:{}}]});return{entity_id:e,source_name:r,events:n,page:Number.isInteger(t.page)&&Number(t.page)>=0?Number(t.page):0,last:t.last===!0}}async function We(s,t,e){let r=await s.callWS({type:"my_dom_ru/history",entity_id:t,page:e}),i=Ct(r);if(i.entity_id!==t)throw new Error("History response entity does not match the request");return i}function ae(s,t){let e=new Map;for(let r of[...s,...t])e.set(`${r.feed_id}:${r.event_id}`,r);return[...e.values()].sort((r,i)=>i.occurred_at-r.occurred_at)}function Fe(s,t,e){let r=new Set(e);return ae(s.filter(i=>!r.has(i.feed_id)),t)}function $e(s,t=!1){let e=new Map;for(let r of s){let i=r.source_name||r.feed_name,n=t&&r.feed_name&&r.feed_name!==i?`${i} \xB7 ${r.feed_name}`:i;r.source_key&&n&&e.set(r.source_key,{key:r.source_key,label:n})}return[...e.values()].sort((r,i)=>r.label.localeCompare(i.label,"ru"))}function Ke(s,t){return t?s.filter(e=>e.source_key===t):[...s]}function Ge(s,t,e){return s.flatMap(r=>{if(e)return[{entityId:r,page:0}];let i=t.get(r);return i?.last?[]:[{entityId:r,page:i?i.page+1:0}]})}function Ye(s,t,e){let r=new Intl.DateTimeFormat("en-CA",{year:"numeric",month:"2-digit",day:"2-digit",timeZone:e}),i=new Intl.DateTimeFormat(t==="en"?"en-US":"ru-RU",{weekday:"long",day:"numeric",month:"long",timeZone:e}),n=new Map;for(let a of[...s].sort((l,o)=>o.occurred_at-l.occurred_at)){let l=new Date(a.occurred_at*1e3),o=r.format(l),h=n.get(o)??{key:o,label:i.format(l),events:[]};h.events.push(a),n.set(o,h)}return[...n.values()]}function Xe(s,t,e){return new Intl.DateTimeFormat(t==="en"?"en-US":"ru-RU",{hour:"2-digit",minute:"2-digit",timeZone:e}).format(new Date(s*1e3))}function Je(s){if(!we(s))throw new Error("mdr-event-history-card: \u0443\u043A\u0430\u0436\u0438\u0442\u0435 'entity' \u0438\u043B\u0438 'entities'");let t=[...typeof s.entity=="string"&&s.entity?[s.entity]:[],...Array.isArray(s.entities)?s.entities:[]],e=[...new Set(t)];if(!e.length)throw new Error("mdr-event-history-card: \u0443\u043A\u0430\u0436\u0438\u0442\u0435 'entity' \u0438\u043B\u0438 'entities'");if(e.some(r=>typeof r!="string"||!r.startsWith("event.")))throw new Error("mdr-event-history-card: \u0432\u0441\u0435 'entity' \u0434\u043E\u043B\u0436\u043D\u044B \u0431\u044B\u0442\u044C event-\u0441\u0443\u0449\u043D\u043E\u0441\u0442\u044F\u043C\u0438");return{entities:e,...typeof s.title=="string"&&s.title?{title:s.title}:{}}}function oe(s){return Tt[s]}var M=w`
  :host {
    --mdr-primary: var(--primary-color, #03a9f4);
    --mdr-success: var(--success-color, #4caf50);
    --mdr-error: var(--error-color, #ef5350);
    --mdr-warning: var(--warning-color, #ffb300);
    --mdr-text: var(--primary-text-color, #e8e8e8);
    --mdr-text-2: var(--secondary-text-color, #a6a6a6);
    --mdr-text-3: var(--disabled-text-color, #787878);
    --mdr-elevated: var(--secondary-background-color, #2a2a2a);
    --mdr-card: var(--ha-card-background, var(--card-background-color, #1c1c1c));
    --mdr-divider: var(--divider-color, #2e2e2e);
    --mdr-on-fill: var(--text-primary-color, #ffffff);
    --mdr-scrim: rgba(0, 0, 0, 0.72);
    --mdr-r-card: 16px;
    --mdr-r-md: 12px;
    --mdr-r-full: 999px;
    --mdr-mono: "Roboto Mono", ui-monospace, monospace;
    /* Тинты бейджей/баннеров = роль-цвет @ ~18% (эквивалент alpha 2E/1A из макета). */
    --mdr-primary-bg: color-mix(in srgb, var(--mdr-primary) 18%, transparent);
    --mdr-success-bg: color-mix(in srgb, var(--mdr-success) 18%, transparent);
    --mdr-error-bg: color-mix(in srgb, var(--mdr-error) 18%, transparent);
    --mdr-warning-bg: color-mix(in srgb, var(--mdr-warning) 18%, transparent);
  }
`,Mt={idle:"var(--mdr-text-2)",ringing:"var(--mdr-warning)",connecting:"var(--mdr-primary)",active:"var(--mdr-success)",ended:"var(--mdr-text-2)",error:"var(--mdr-error)"};function ke(s){return Mt[s]??"var(--mdr-text-2)"}var Ze=[M,w`
    :host {
      display: block;
      container-type: inline-size;
    }
    ha-card {
      overflow: hidden;
      color: var(--mdr-text);
      background: var(--mdr-card);
      border-radius: var(--mdr-r-card);
    }
    header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 20px 20px 12px;
    }
    h2 {
      flex: 1;
      min-width: 0;
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
      font-weight: 600;
    }
    button {
      min-height: 44px;
      border: 0;
      border-radius: var(--mdr-r-full);
      color: var(--mdr-text);
      background: transparent;
      font: inherit;
      cursor: pointer;
    }
    button:focus-visible {
      outline: 2px solid var(--mdr-primary);
      outline-offset: 2px;
    }
    button:disabled {
      opacity: 0.55;
      cursor: default;
    }
    .refresh {
      display: inline-grid;
      width: 44px;
      place-items: center;
    }
    .refresh:hover,
    .refresh:active {
      background: var(--mdr-elevated);
    }
    .refresh mdr-icon {
      --mdr-icon-size: 20px;
    }
    .content {
      padding: 0 16px 16px;
    }
    .filters {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 0 0 4px;
      scrollbar-width: thin;
    }
    .chip {
      min-height: 36px;
      padding: 0 14px;
      flex: none;
      color: var(--mdr-text-2);
      background: var(--mdr-elevated);
      font-size: 13px;
      font-weight: 600;
      white-space: nowrap;
    }
    .chip.active {
      color: var(--mdr-primary);
      background: var(--mdr-primary-bg);
    }
    section + section {
      margin-top: 20px;
    }
    h3 {
      margin: 14px 4px 8px;
      color: var(--mdr-text-2);
      font-size: 14px;
      line-height: 1.4;
      font-weight: 600;
      text-transform: capitalize;
    }
    .events {
      overflow: hidden;
      margin: 0;
      padding: 0;
      border: 1px solid var(--mdr-divider);
      border-radius: var(--mdr-r-md);
      list-style: none;
    }
    .event {
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      align-items: center;
      gap: 12px;
      min-height: 72px;
      padding: 8px 12px;
      box-sizing: border-box;
    }
    .event + .event {
      border-top: 1px solid var(--mdr-divider);
    }
    .event-icon {
      display: grid;
      width: 44px;
      height: 44px;
      place-items: center;
      border-radius: var(--mdr-r-md);
      color: var(--mdr-success);
      background: var(--mdr-success-bg);
    }
    .event.missed .event-icon {
      color: var(--mdr-error);
      background: var(--mdr-error-bg);
    }
    .event-icon mdr-icon {
      --mdr-icon-size: 22px;
    }
    .event-copy {
      display: flex;
      min-width: 0;
      flex-direction: column;
      gap: 3px;
    }
    .event-title {
      overflow: hidden;
      font-size: 15px;
      line-height: 1.3;
      font-weight: 600;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .source {
      overflow: hidden;
      color: var(--mdr-text-2);
      font-size: 13px;
      line-height: 1.3;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    time {
      color: var(--mdr-text-2);
      font-size: 13px;
      font-variant-numeric: tabular-nums;
    }
    .state {
      display: grid;
      min-height: 144px;
      padding: 20px;
      place-items: center;
      color: var(--mdr-text-2);
      text-align: center;
    }
    .state.error {
      gap: 8px;
      color: var(--mdr-error);
    }
    .retry,
    .more {
      padding: 0 18px;
      color: var(--mdr-primary);
      background: var(--mdr-primary-bg);
      font-weight: 600;
    }
    footer {
      display: flex;
      padding-top: 16px;
      justify-content: center;
    }
    .inline-error {
      margin: 12px 4px 0;
      color: var(--mdr-error);
      font-size: 13px;
      text-align: center;
    }
    .spin {
      animation: spin 900ms linear infinite;
    }
    .skeleton {
      width: 100%;
    }
    .skeleton-line {
      height: 64px;
      border-radius: var(--mdr-r-md);
      background: var(--mdr-elevated);
      animation: pulse 1.4s ease-in-out infinite alternate;
    }
    .skeleton-line + .skeleton-line {
      margin-top: 8px;
    }
    @container (min-width: 640px) {
      .content {
        padding-right: 20px;
        padding-left: 20px;
      }
      .event {
        min-height: 76px;
        padding-right: 16px;
        padding-left: 16px;
      }
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    @keyframes pulse {
      to { opacity: 0.55; }
    }
    @media (prefers-reduced-motion: reduce) {
      .spin,
      .skeleton-line { animation: none; }
    }
  `];typeof window<"u"&&(window.customCards=window.customCards||[],window.customCards.push({type:"mdr-event-history-card",name:"\u0423\u043C\u043D\u044B\u0439 \u0414\u043E\u043C.\u0440\u0443 \u2014 \u0418\u0441\u0442\u043E\u0440\u0438\u044F \u0441\u043E\u0431\u044B\u0442\u0438\u0439",description:"\u0418\u0441\u0442\u043E\u0440\u0438\u044F \u0432\u044B\u0437\u043E\u0432\u043E\u0432 \u0438 \u043F\u0440\u043E\u0445\u043E\u0434\u043E\u0432 \u043F\u043E \u043A\u043B\u044E\u0447\u0430\u043C \u0441 \u043E\u0431\u043B\u0430\u0447\u043D\u044B\u043C\u0438 \u0438\u043C\u0435\u043D\u0430\u043C\u0438.",preview:!1}));var S=class extends b{constructor(){super(...arguments);this._events=[];this._selectedSource="";this._loading=!1;this._loaded=!1;this._error="";this._loadedEntitiesKey="";this._feedStates=new Map;this._refresh=()=>{this._loading||this._loadPages(!0)};this._more=()=>{!this._loading&&!this._allLast&&this._loadPages(!1)}}setConfig(e){this._config=Je(e)}getCardSize(){return 5}static getStubConfig(){return{entities:["event.account_123456_place_7890_event_history"]}}updated(e){if(!e.has("hass")&&!e.has("_config"))return;let r=this._config?.entities,i=r?.join("\0")??"";!this.hass||!r?.length||i===this._loadedEntitiesKey||(this._loadedEntitiesKey=i,this._events=[],this._selectedSource="",this._feedStates=new Map,this._loaded=!1,this._loadPages(!0))}get _lang(){return ne(this.hass)}get _allLast(){let e=this._config?.entities??[];return e.length>0&&e.every(r=>this._feedStates.get(r)?.last===!0)}async _loadPages(e){let r=this.hass,i=this._config?.entities;if(!r||!i?.length)return;let n=i.join("\0"),a=Ge(i,this._feedStates,e);if(a.length){this._loading=!0,this._error="";try{let l=await Promise.allSettled(a.map(({entityId:v,page:y})=>We(r,v,y)));if(this._loadedEntitiesKey!==n)return;let o=[],h=!1,g=!1,u=[];if(l.forEach((v,y)=>{if(v.status==="rejected"){h=!0;return}g=!0,o=ae(o,v.value.events);let P=a[y]?.entityId;P&&(u.push(P),this._feedStates.set(P,{page:v.value.page,last:v.value.last}))}),g){this._events=e?Fe(this._events,o,u):ae(this._events,o);let v=$e(this._events,i.length>1);this._selectedSource&&!v.some(y=>y.key===this._selectedSource)&&(this._selectedSource="")}h&&(this._error=oe(this._lang).unavailable),this._loaded=!0}catch{this._loadedEntitiesKey===n&&(this._error=oe(this._lang).unavailable)}finally{this._loadedEntitiesKey===n&&(this._loading=!1,this._loaded=!0)}}}render(){let e=oe(this._lang),r=$e(this._events,(this._config?.entities.length??0)>1),i=Ke(this._events,this._selectedSource),n=Ye(i,this._lang);return c`
      <ha-card>
        <header>
          <h2>${this._config?.title??e.title}</h2>
          <button
            class="refresh"
            aria-label=${e.refresh}
            title=${e.refresh}
            ?disabled=${this._loading}
            @click=${this._refresh}
          ><mdr-icon class=${this._loading?"spin":""} name="refresh-cw"></mdr-icon></button>
        </header>
        <div class="content" aria-live="polite">
          ${r.length>1?this._renderFilters(r,e):p}
          ${this._renderBody(n,e,r)}
          ${this._loaded&&this._error?c`<p class="inline-error" role="alert">${this._error}</p>`:p}
          ${this._loaded&&!this._allLast?c`<footer><button class="more" ?disabled=${this._loading} @click=${this._more}>
                ${this._loading?e.loading:e.more}
              </button></footer>`:p}
        </div>
      </ha-card>
    `}_renderBody(e,r,i){return!this._loaded&&this._loading?c`<div class="state" role="status" aria-label=${r.loading}>
        <div class="skeleton"><div class="skeleton-line"></div><div class="skeleton-line"></div></div>
      </div>`:!this._events.length&&this._error?c`<div class="state error" role="alert">
        <span>${this._error}</span>
        <button class="retry" @click=${this._refresh}>${r.retry}</button>
      </div>`:e.length?c`${e.map(n=>c`
      <section aria-labelledby="day-${n.key}">
        <h3 id="day-${n.key}">${n.label}</h3>
        <ul class="events">
          ${n.events.map(a=>this._renderEvent(a,r,i))}
        </ul>
      </section>
    `)}`:c`<div class="state">${r.empty}</div>`}_renderEvent(e,r,i){let n=e.event_type==="call_missed",a=e.event_type==="key_activated",l=new Date(e.occurred_at*1e3),o=i.find(h=>h.key===e.source_key)?.label??e.source_name;return c`<li class="event ${n?"missed":"accepted"}">
      <span class="event-icon"><mdr-icon name=${a?"key-round":n?"phone-off":"phone"}></mdr-icon></span>
      <span class="event-copy">
        <span class="event-title">${r.event[e.event_type]}</span>
        ${a&&e.key_name?c`<span class="source">${e.key_name}</span>`:p}
        ${o?c`<span class="source">${o}</span>`:p}
      </span>
      <time datetime=${l.toISOString()}>${Xe(e.occurred_at,this._lang)}</time>
    </li>`}_renderFilters(e,r){return c`<div class="filters" aria-label=${r.devices}>
      <button
        class="chip ${this._selectedSource?"":"active"}"
        aria-pressed=${this._selectedSource?"false":"true"}
        @click=${()=>{this._selectedSource=""}}
      >${r.allDevices}</button>
      ${e.map(i=>c`<button
        class="chip ${this._selectedSource===i.key?"active":""}"
        aria-pressed=${this._selectedSource===i.key?"true":"false"}
        @click=${()=>{this._selectedSource=i.key}}
      >${i.label}</button>`)}
    </div>`}};S.styles=Ze,d([m({attribute:!1})],S.prototype,"hass",2),d([f()],S.prototype,"_config",2),d([f()],S.prototype,"_events",2),d([f()],S.prototype,"_selectedSource",2),d([f()],S.prototype,"_loading",2),d([f()],S.prototype,"_loaded",2),d([f()],S.prototype,"_error",2),S=d([k("mdr-event-history-card")],S);var Ht=new Set(["idle","ringing","connecting","active","ended","error"]);function Qe(s){return s&&Ht.has(s)?s:"idle"}var B={visible:!1,video:"none",actions:[],showOpen:!1,showTimer:!1,showAnswerWindow:!1,busy:!1,isError:!1};function et(s){switch(s){case"ringing":return{...B,visible:!0,video:"doorbell",actions:["reject","accept"],showOpen:!0,showAnswerWindow:!0};case"connecting":return{...B,visible:!0,video:"doorbell",actions:["cancel","connecting"],showOpen:!0,busy:!0};case"active":return{...B,visible:!0,video:"call",actions:["mic","sound","hangup"],showOpen:!0,showTimer:!0};case"error":return{...B,visible:!0,video:"none",actions:["retry","hangup"],showOpen:!0,isError:!0};case"ended":return{...B,visible:!0,video:"call",actions:["close"],showOpen:!0};default:return{...B}}}function tt(s,t){if(s==="call")return t.camera;if(s==="doorbell")return t.doorbell_camera??t.camera}var E=class extends b{constructor(){super(...arguments);this.muted=!1;this.uiLang="ru";this._provider="pending"}connectedCallback(){super.connectedCallback(),this._resolveProvider()}async _resolveProvider(){if(customElements.get("ha-camera-stream")){this._provider="ha";return}try{let e=await window.loadCardHelpers?.();e&&!customElements.get("ha-camera-stream")&&(e.createCardElement({type:"picture-glance",entities:[]}),await new Promise(r=>{let i=setTimeout(r,5e3);customElements.whenDefined("ha-camera-stream").then(()=>{clearTimeout(i),r()})}))}catch{}customElements.get("ha-camera-stream")?this._provider="ha":customElements.get("webrtc-camera")?this._provider="webrtc":this._provider="none"}updated(e){this._provider==="webrtc"&&this._syncWebrtc(e)}_syncWebrtc(e){let r=this.renderRoot.querySelector("#webrtc-host");if(!(!r||!this.entity||!this.hass))if(e.has("entity")||e.has("_provider")||e.has("muted")||!this._webrtcEl||this._webrtcEl.parentElement!==r){r.replaceChildren();let i=document.createElement("webrtc-camera");i.setConfig({entity:this.entity,muted:this.muted}),i.hass=this.hass,r.appendChild(i),this._webrtcEl=i}else this._webrtcEl.hass=this.hass}render(){let e=_(this.uiLang).video;if(!this.entity||!this.hass)return this._frame("video-off",e.noVideo);let r=this.hass.states[this.entity];if(!r)return this._frame("video-off",e.cameraUnavailable);switch(this._provider){case"pending":return this._frame("video-off",e.loading);case"ha":return c`
          <ha-camera-stream
            .hass=${this.hass}
            .stateObj=${r}
            .muted=${this.muted}
          ></ha-camera-stream>
        `;case"webrtc":return c`<div id="webrtc-host"></div>`;default:return this._frame("video-off",e.playerUnavailable)}}_frame(e,r){return c`
      <div class="frame" role="img" aria-label=${r}>
        <mdr-icon name=${e}></mdr-icon>
        <span>${r}</span>
      </div>
      ${p}
    `}};E.styles=w`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }
    ha-camera-stream,
    #webrtc-host {
      display: block;
      width: 100%;
      height: 100%;
    }
    /* реальный плеер заполняет область (object-fit самого видео — по потоку) */
    .frame {
      width: 100%;
      height: 100%;
      background: var(--secondary-background-color);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      color: var(--secondary-text-color);
      text-align: center;
      padding: 8px;
      box-sizing: border-box;
    }
    .frame mdr-icon {
      --mdr-icon-size: 40px;
    }
    .frame span {
      font-size: 0.85rem;
    }
  `,d([m({attribute:!1})],E.prototype,"hass",2),d([m()],E.prototype,"entity",2),d([m({type:Boolean})],E.prototype,"muted",2),d([m()],E.prototype,"uiLang",2),d([f()],E.prototype,"_provider",2),E=d([k("mdr-call-video")],E);function Lt(s){switch(s){case"camera_off":return"placeholder-camera";case"connection_lost":return"placeholder-connection";case"ended":return"video-dimmed";default:return"video"}}var $=class extends b{constructor(){super(...arguments);this.muted=!1;this.live=!1;this.soundOff=!1;this.stageState="live";this.audioBlocked=!1;this.uiLang="ru";this._unmute=()=>{this.dispatchEvent(new CustomEvent("unmute",{bubbles:!0,composed:!0}))}}render(){let e=_(this.uiLang),r=Lt(this.stageState);return r==="placeholder-camera"?this._placeholder("video-off","muted",e.stage.cameraOff.title,e.stage.cameraOff.sub):r==="placeholder-connection"?this._placeholder("wifi-off","err",e.stage.connectionLost.title,e.stage.connectionLost.sub):c`
      <mdr-call-video .hass=${this.hass} .uiLang=${this.uiLang} .entity=${this.entity} .muted=${this.muted}></mdr-call-video>
      ${r==="video-dimmed"?c`<div class="dim" aria-hidden="true"></div>`:p}
      <div class="top">
        ${this.live?c`<span class="live"><span class="live-dot" aria-hidden="true"></span>LIVE</span>`:p}
        ${this.soundOff?c`<span class="chip"><mdr-icon name="volume-x"></mdr-icon>${e.stage.soundOffChip}</span>`:p}
      </div>
      ${this.audioBlocked?c`
            <button class="tap" @click=${this._unmute} aria-label=${e.stage.unmuteAria}></button>
            <span class="cta" aria-hidden="true">
              <mdr-icon name="volume-x"></mdr-icon>${e.stage.unmuteCta}
            </span>
          `:p}
    `}_placeholder(e,r,i,n){return c`
      <div class="fallback ${r}" role="img" aria-label=${i}>
        <mdr-icon name=${e}></mdr-icon>
        <span class="fb-title">${i}</span>
        <span class="fb-sub">${n}</span>
      </div>
    `}};$.styles=[M,w`
      :host {
        position: absolute;
        inset: 0;
        display: block;
      }
      mdr-call-video {
        position: absolute;
        inset: 0;
      }
      .dim {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
      }
      /* верхний ряд оверлеев: LIVE (слева) + чип звука (справа) */
      .top {
        position: absolute;
        top: calc(12px * var(--mdr-scale, 1));
        left: calc(12px * var(--mdr-scale, 1));
        right: calc(12px * var(--mdr-scale, 1));
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        pointer-events: none;
      }
      .live {
        display: inline-flex;
        align-items: center;
        gap: calc(6px * var(--mdr-scale, 1));
        padding: calc(3px * var(--mdr-scale, 1)) calc(9px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: rgba(211, 47, 47, 0.88);
        color: #fff;
        font-size: calc(10px * var(--mdr-scale, 1));
        font-weight: 600;
        letter-spacing: 0.04em;
      }
      .live-dot {
        width: calc(6px * var(--mdr-scale, 1));
        height: calc(6px * var(--mdr-scale, 1));
        border-radius: 50%;
        background: #fff;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: calc(6px * var(--mdr-scale, 1));
        padding: calc(5px * var(--mdr-scale, 1)) calc(10px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: rgba(0, 0, 0, 0.63);
        color: #fff;
        font-size: calc(11px * var(--mdr-scale, 1));
      }
      .chip mdr-icon {
        --mdr-icon-size: calc(14px * var(--mdr-scale, 1));
      }
      /* CTA «включить звук» + прозрачный tap-слой поверх всего видео */
      .tap {
        position: absolute;
        inset: 0;
        border: none;
        background: transparent;
        cursor: pointer;
        z-index: 2;
      }
      /* CTA — в НИЖНЕЙ части видео (не перекрывает лицо звонящего), UX §8/§13 */
      .cta {
        position: absolute;
        left: 50%;
        bottom: calc(16px * var(--mdr-scale, 1));
        transform: translateX(-50%);
        display: inline-flex;
        align-items: center;
        gap: calc(8px * var(--mdr-scale, 1));
        padding: calc(10px * var(--mdr-scale, 1)) calc(18px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: var(--mdr-scrim);
        color: #fff;
        font-size: calc(13px * var(--mdr-scale, 1));
        font-weight: 500;
        white-space: nowrap;
        z-index: 3;
        pointer-events: none;
      }
      .cta mdr-icon {
        --mdr-icon-size: calc(18px * var(--mdr-scale, 1));
      }
      /* плейсхолдеры (камера недоступна / связь прервана) */
      .fallback {
        position: absolute;
        inset: 0;
        background: var(--mdr-card);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: calc(6px * var(--mdr-scale, 1));
        text-align: center;
        padding: calc(12px * var(--mdr-scale, 1));
        box-sizing: border-box;
      }
      .fallback mdr-icon {
        --mdr-icon-size: calc(36px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
      }
      .fallback.err mdr-icon {
        color: var(--mdr-error);
      }
      .fb-title {
        font-size: calc(15px * var(--mdr-scale, 1));
        color: var(--mdr-text);
      }
      .fb-sub {
        font-size: calc(12px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
      }
    `],d([m({attribute:!1})],$.prototype,"hass",2),d([m()],$.prototype,"entity",2),d([m({type:Boolean})],$.prototype,"muted",2),d([m({type:Boolean})],$.prototype,"live",2),d([m({type:Boolean})],$.prototype,"soundOff",2),d([m()],$.prototype,"stageState",2),d([m({type:Boolean})],$.prototype,"audioBlocked",2),d([m()],$.prototype,"uiLang",2),$=d([k("mdr-call-stage")],$);function it(s){return s<0?0:s>1?1:s}function Ot(s,t,e,r){let i=Math.max(1,e-r);return it((s-t-r/2)/i)}function Ut(s,t){return it(s/Math.max(1,t))}var Dt=.92,Nt=800,rt=68,A=class extends b{constructor(){super(...arguments);this.mode="hold";this.disabled=!1;this.label="";this.uiLang="ru";this.status="idle";this._progress=0;this._arming=!1;this._raf=0;this._holdStart=0;this._trackRect=null;this._knobW=rt;this._pointerId=null;this._committed=!1;this._holdTick=()=>{if(this._blocked||!this._arming){this._reset();return}if(this._progress=Ut(performance.now()-this._holdStart,Nt),this._progress>=1){this._commit();return}this._raf=requestAnimationFrame(this._holdTick)};this._onHoldDown=e=>{this._blocked||this._arming||e.button!==0||(this._pointerId=e.pointerId,e.currentTarget.setPointerCapture?.(e.pointerId),this._arming=!0,this._holdStart=performance.now(),this._raf=requestAnimationFrame(this._holdTick))};this._onHoldUp=e=>{e.pointerId===this._pointerId&&this._progress<1&&this._reset()};this._onPointerCancel=e=>{e.pointerId===this._pointerId&&this._reset()};this._onSlideDown=e=>{if(this._blocked||this._arming||e.button!==0)return;this._pointerId=e.pointerId;let r=e.currentTarget.closest(".track");this._trackRect=r?.getBoundingClientRect()??null;let i=r?.querySelector(".knob");this._knobW=i?.getBoundingClientRect().width||rt,e.currentTarget.setPointerCapture?.(e.pointerId),this._arming=!0};this._onSlideMove=e=>{this._blocked||!this._arming||!this._trackRect||e.pointerId!==this._pointerId||(this._progress=Ot(e.clientX,this._trackRect.left,this._trackRect.width,this._knobW))};this._onSlideUp=e=>{!this._arming||e.pointerId!==this._pointerId||(this._progress>=Dt?this._commit():this._reset())};this._onTap=()=>{this._fireOpen()}}get _ariaLabel(){return this.label||_(this.uiLang).open.labelDefault}get _blocked(){return this.disabled||this._committed||this.status==="opening"||this.status==="opened"}disconnectedCallback(){super.disconnectedCallback(),this._reset()}updated(e){e.has("status")&&(this.status==="idle"||this.status==="error")&&(this._committed=!1,this._reset()),(e.has("disabled")&&this.disabled||e.has("mode"))&&this._reset()}_fireOpen(){this._blocked||(this._committed=!0,this.dispatchEvent(new CustomEvent("open",{bubbles:!0,composed:!0})))}_reset(){this._raf&&cancelAnimationFrame(this._raf),this._raf=0,this._arming=!1,this._progress=0,this._trackRect=null,this._pointerId=null}_commit(){if(this._blocked||!this._arming){this._reset();return}this._raf&&cancelAnimationFrame(this._raf),this._raf=0,this._arming=!1,this._progress=1,this._trackRect=null,this._pointerId=null,this._fireOpen()}render(){let e=this.mode==="tap"?this._renderTap():this.mode==="slide"?this._renderSlide():this._renderHold();return c`
      <div class="wrap" style="--mdr-prog:${this._vp()}">
        ${e}
        ${this._caption()}
      </div>
    `}_caption(){let e=_(this.uiLang).open,r="",i="";return this.status==="opened"?(r=e.captionOpened,i="st-opened"):this.status==="error"?(r=e.captionError,i="st-error"):this.status==="opening"?r="":this.mode==="slide"&&(r=e.captionSlideHint),c`<span class="caption ${i}">${r||c`&nbsp;`}</span>`}_labelText(){let e=_(this.uiLang).open;return this.status==="opened"?e.opened:this.status==="opening"?e.opening:this.mode==="slide"?e.slide:e.hold}_barIcon(){return this.status==="opening"?"loader-circle":this.status==="opened"?"lock-open":"key-round"}_knobIcon(){return this.status==="opening"?"loader-circle":"key-round"}_vp(){return this.status==="opening"||this.status==="opened"?1:this._progress}_statusClass(){return this.status==="opened"?"st-opened":this.status==="opening"?"st-opening":this.status==="error"?"st-error":""}_renderTap(){return c`
      <button class="pill tap ${this._statusClass()}" ?disabled=${this._blocked} @click=${this._onTap}
              aria-label=${this._ariaLabel}>
        <div class="fill"></div>
        <span class="content"><mdr-icon name=${this._barIcon()}></mdr-icon>${this._labelText()}</span>
      </button>
    `}_renderHold(){return c`
      <button
        class="pill hold ${this._arming?"arming":""} ${this._statusClass()}"
        ?disabled=${this._blocked}
        aria-label="${this._ariaLabel} ${_(this.uiLang).open.holdAriaSuffix}"
        @pointerdown=${this._onHoldDown}
        @pointerup=${this._onHoldUp}
        @pointercancel=${this._onPointerCancel}
        @lostpointercapture=${this._onPointerCancel}
        @pointerleave=${this._onHoldUp}
      >
        <div class="fill"></div>
        <span class="content"><mdr-icon name=${this._barIcon()}></mdr-icon>${this._labelText()}</span>
      </button>
    `}_renderSlide(){return c`
      <div
        class="track ${this._statusClass()} ${this._arming?"dragging":""}"
        role="slider"
        aria-label=${this._ariaLabel}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow=${Math.round(this._vp()*100)}
        aria-disabled=${this._blocked?"true":"false"}
      >
        <mdr-icon class="lock-under" name="lock"></mdr-icon>
        <mdr-icon class="end" name="lock-open"></mdr-icon>
        <div class="fill"></div>
        <span class="label">${this._labelText()}</span>
        <div
          class="knob ${this.disabled?"off":""} ${this.status==="opening"?"loading":""}"
          @pointerdown=${this._onSlideDown}
          @pointermove=${this._onSlideMove}
          @pointerup=${this._onSlideUp}
          @pointercancel=${this._onPointerCancel}
          @lostpointercapture=${this._onPointerCancel}
        >
          <mdr-icon name=${this._knobIcon()}></mdr-icon>
        </div>
      </div>
    `}};A.styles=[M,w`
      :host {
        display: block;
      }
      .wrap {
        display: flex;
        flex-direction: column;
        gap: calc(8px * var(--mdr-scale, 1));
        align-items: center;
        width: 100%;
      }
      /* ---- общая заливка-прогресс ---- */
      .fill {
        position: absolute;
        inset: 0 auto 0 0;
        width: calc(var(--mdr-prog, 0) * 100%);
        background: var(--mdr-primary);
        opacity: 0.15;
        transition: width 0.2s ease;
      }
      /* ---- slide: трек 300×80 в масштабе 1 (макет: центрирован, не на всю
         ширину); при --mdr-scale трек/ключ растут пропорционально, ширина не
         превышает контейнер (min(...,100%)) — на панели слайдер крупный ---- */
      .track {
        position: relative;
        width: min(calc(300px * var(--mdr-scale, 1)), 100%);
        height: calc(80px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: var(--mdr-elevated);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        touch-action: none;
        user-select: none;
      }
      /* в покое заливки нет (иначе «залипло»); появляется только при перетаскивании */
      .track .fill {
        width: 0;
      }
      /* при drag правый край заливки строго = центр ключа (не обгоняет) */
      .track.dragging .fill {
        width: calc(
          40px * var(--mdr-scale, 1) + var(--mdr-prog, 0) * (100% - 80px * var(--mdr-scale, 1))
        );
        transition: none;
      }
      /* открытие (loading): доведено до конца — заливка на всю ширину + пульс */
      .track.st-opening .fill {
        width: 100%;
        background: var(--mdr-primary);
        opacity: 0.15;
        animation: mdr-pulse 1.1s ease-in-out infinite;
      }
      /* закрытый замок под ключом (проявляется при отъезде): иконка 20, центр под ключом */
      .lock-under {
        position: absolute;
        left: calc(30px * var(--mdr-scale, 1));
        top: 50%;
        transform: translateY(-50%);
        --mdr-icon-size: calc(20px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
        z-index: 0;
      }
      /* торец: открытый замок (макет: иконка 20, центр 28px от правого края) */
      .end {
        position: absolute;
        right: calc(18px * var(--mdr-scale, 1));
        top: 50%;
        transform: translateY(-50%);
        --mdr-icon-size: calc(20px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
        z-index: 0;
      }
      .track .label {
        position: relative;
        z-index: 1;
        font-size: calc(17px * var(--mdr-scale, 1));
        font-weight: 600;
        color: var(--mdr-text);
      }
      .knob {
        position: absolute;
        top: calc(6px * var(--mdr-scale, 1));
        left: calc(6px * var(--mdr-scale, 1) + var(--mdr-prog, 0) * (100% - 80px * var(--mdr-scale, 1)));
        width: calc(68px * var(--mdr-scale, 1));
        height: calc(68px * var(--mdr-scale, 1));
        border-radius: 50%;
        background: var(--mdr-primary);
        color: var(--mdr-on-fill);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: grab;
        touch-action: none;
        z-index: 2;
        --mdr-icon-size: calc(28px * var(--mdr-scale, 1));
        transition: left 0.18s ease;
      }
      .track.dragging .knob {
        transition: none;
        cursor: grabbing;
      }
      .knob.off {
        opacity: 0.5;
      }
      /* slide success: зелёный трек + «Открыто» + ключ справа */
      .track.st-opened .fill {
        background: var(--mdr-success);
        opacity: 1;
        width: 100%;
      }
      .track.st-opened .label {
        color: var(--mdr-on-fill);
      }
      .track.st-opened .knob {
        background: var(--mdr-success);
      }
      /* success: ключ-knob уехал вправо и накрыл торец — торец прячем */
      .track.st-opened .end {
        display: none;
      }
      /* ---- hold/tap: outlined-пилюля, контент неподвижен, заливка бежит ---- */
      .pill {
        position: relative;
        width: 100%;
        min-height: calc(64px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        border: 2px solid var(--mdr-primary);
        background: transparent;
        color: var(--mdr-text);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        cursor: pointer;
        touch-action: none;
        user-select: none;
        font: inherit;
        padding: 0 calc(16px * var(--mdr-scale, 1));
      }
      .pill.arming .fill {
        transition: none;
      }
      .pill .fill {
        opacity: 0.2;
      }
      .pill .content {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: calc(8px * var(--mdr-scale, 1));
        font-size: calc(17px * var(--mdr-scale, 1));
        font-weight: 600;
        --mdr-icon-size: calc(24px * var(--mdr-scale, 1));
      }
      .pill[disabled] {
        opacity: 0.5;
        cursor: not-allowed;
      }
      .pill.st-opened {
        border-color: var(--mdr-success);
      }
      .pill.st-opened .fill {
        background: var(--mdr-success);
        opacity: 1;
        width: 100%;
      }
      .pill.st-opened .content {
        color: var(--mdr-on-fill);
      }
      /* ---- подпись под контролом ---- */
      .caption {
        font-size: calc(12px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
        text-align: center;
      }
      .caption.st-opened {
        color: var(--mdr-success);
      }
      .caption.st-error {
        color: var(--mdr-error);
      }
      /* спиннер на ключе слайдера / иконке пилюли во время открытия */
      .knob.loading mdr-icon,
      .pill.st-opening .content mdr-icon {
        animation: mdr-spin 0.8s linear infinite;
      }
      @keyframes mdr-spin {
        to {
          transform: rotate(360deg);
        }
      }
      @keyframes mdr-pulse {
        0%,
        100% {
          opacity: 0.12;
        }
        50% {
          opacity: 0.26;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .fill,
        .knob {
          transition: none;
        }
        .knob.loading mdr-icon,
        .pill.st-opening .content mdr-icon,
        .track.st-opening .fill {
          animation: none;
        }
      }
    `],d([m()],A.prototype,"mode",2),d([m({type:Boolean})],A.prototype,"disabled",2),d([m()],A.prototype,"label",2),d([m()],A.prototype,"uiLang",2),d([m()],A.prototype,"status",2),d([f()],A.prototype,"_progress",2),d([f()],A.prototype,"_arming",2),A=d([k("mdr-open-control")],A);function st(s,t,e=!1){return!t||s==="denied"?!1:s==="granted"||e}function nt(s,t,e){return s?t==="denied"?"denied":t==="prompt"&&!e?"prompt":"none":"no_https"}var X=class X{constructor(t,e=()=>{}){this._getConn=t;this._onChange=e;this.active=!1;this.lastError=""}hasGrantedBefore(){try{return typeof localStorage<"u"&&localStorage.getItem(X._GRANT_KEY)==="1"}catch{return!1}}markGranted(){try{typeof localStorage<"u"&&localStorage.setItem(X._GRANT_KEY,"1")}catch{}}async queryPermission(){try{return(await navigator.permissions?.query({name:"microphone"}))?.state??"unknown"}catch{return"unknown"}}get secure(){return typeof window<"u"&&window.isSecureContext===!0}async start(){if(this.active)return;let t=this._getConn();if(!t){this._fail("\u043D\u0435\u0442 \u0441\u0432\u044F\u0437\u0438 \u0441 Home Assistant");return}if(!navigator.mediaDevices?.getUserMedia){this._fail("\u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D \u043D\u0435\u0434\u043E\u0441\u0442\u0443\u043F\u0435\u043D (\u043D\u0443\u0436\u0435\u043D HTTPS-origin)");return}try{let e=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:!0,noiseSuppression:!0,autoGainControl:!0}}),r=window.AudioContext||window.webkitAudioContext,i=new r,n=i.sampleRate,a=this._sub;(!a||a.sampleRate!==n)&&(a={handlerId:(await t.sendMessagePromise({type:"my_dom_ru/intercom_uplink",sample_rate:n})).handler_id,sampleRate:n},this._sub=a);let l=a.handlerId,o=t.socket;await i.audioWorklet.addModule(this._workletUrl());let h=new AudioWorkletNode(i,"mdr-pcm-int16",{numberOfOutputs:0});h.port.onmessage=u=>{let v=u.data,y=new Uint8Array(1+v.byteLength);y[0]=l,y.set(new Uint8Array(v.buffer),1),o.readyState===1&&o.send(y)};let g=i.createMediaStreamSource(e);g.connect(h),this._ctx={ac:i,stream:e,node:h,src:g},this.active=!0,this.lastError="",this.markGranted(),this._onChange()}catch(e){this._fail(e instanceof Error?e.message:String(e))}}stop(){let t=this._ctx;if(t){try{t.node.port.onmessage=null,t.node.disconnect(),t.src.disconnect()}catch{}try{t.stream.getTracks().forEach(e=>e.stop())}catch{}try{t.ac.close()}catch{}}if(this._ctx=void 0,this.active=!1,this._wUrl){try{URL.revokeObjectURL(this._wUrl)}catch{}this._wUrl=void 0}this._onChange()}_fail(t){this.lastError=t,this.stop()}_workletUrl(){if(this._wUrl)return this._wUrl;let t=`
      class EgPcmInt16 extends AudioWorkletProcessor {
        process(inputs) {
          const ch = inputs[0] && inputs[0][0];
          if (ch && ch.length) {
            const i16 = new Int16Array(ch.length);
            for (let i = 0; i < ch.length; i++) {
              const s = Math.max(-1, Math.min(1, ch[i]));
              i16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
            }
            this.port.postMessage(i16, [i16.buffer]);
          }
          return true;
        }
      }
      registerProcessor("mdr-pcm-int16", EgPcmInt16);`;return this._wUrl=URL.createObjectURL(new Blob([t],{type:"application/javascript"})),this._wUrl}};X._GRANT_KEY="mdr-intercom-mic-granted";var ce=X;var zt=new Set(["slide","hold","tap"]);function at(s,t){return s&&zt.has(s)?s:t?"slide":"hold"}function ot(){return typeof window<"u"&&typeof window.matchMedia=="function"&&window.matchMedia("(pointer: coarse)").matches}var le=new Set(["ringing","connecting","active","error"]),Bt=6e3,jt=3e3,ct=3e4,It=2500,x=class extends b{constructor(){super(...arguments);this._config={};this._muted=!1;this._audioBlocked=!1;this._micActive=!1;this._micPerm="unknown";this._openStatus="idle";this._now=Date.now();this._ringingSince=0;this._errDismissed=new Set;this._endedEntity="";this._endedDuration="";this._doorbells=[];this._openAction="hold";this._prevKey="";this._prevPhases=new Map;this._mic=new ce(()=>this.hass?.connection,()=>{this._micActive=this._mic.active,this.requestUpdate()});this._clearEnded=()=>{this._endedHide&&(clearTimeout(this._endedHide),this._endedHide=void 0),this._endedEntity="",this.requestUpdate()};this._unmute=()=>{this._muted=!1,this._audioBlocked=!1};this._answer=()=>{this.hass?.callService("my_dom_ru","answer")};this._hangup=()=>{this.hass?.callService("my_dom_ru","hangup")};this._toggleMute=()=>{this._muted=!this._muted};this._toggleMic=async()=>{this._mic.active?this._mic.stop():await this._mic.start(),this._micPerm=await this._mic.queryPermission()};this._open=async()=>{let e=this._active?.lock;if(!(!e||!this.hass||this._openStatus==="opening"||this._openStatus==="opened")){this._openStatus="opening";try{await this.hass.callService("lock","unlock",{entity_id:e}),this._openStatus="opened"}catch{this._openStatus="error"}this._openReset&&clearTimeout(this._openReset),this._openReset=window.setTimeout(()=>{this._openStatus="idle",this.requestUpdate()},jt)}};this._dismiss=()=>{this.dispatchEvent(new CustomEvent("mdr-dismiss",{bubbles:!0,composed:!0}))};this._retry=()=>{this.hass?.callService("my_dom_ru","answer")}}setConfig(e){let r=e?.doorbells??(e?.call_state?[{call_state:e.call_state,doorbell_camera:e.doorbell_camera,lock:e.lock,name:e.name,address:e.address}]:[]);if(!r.length||r.some(i=>!i.call_state))throw new Error("mdr-intercom-call-card: \u0443\u043A\u0430\u0436\u0438\u0442\u0435 'doorbells' (\u0441 call_state) \u0438\u043B\u0438 'call_state'");this._config=e,this._doorbells=r,this._openAction=at(e.open_action,ot())}getCardSize(){return 8}static getStubConfig(){return{camera:"",doorbells:[{call_state:"",doorbell_camera:"",lock:""}]}}disconnectedCallback(){super.disconnectedCallback(),this._mic.stop(),this._stopTick(),this._errHide&&clearTimeout(this._errHide),this._openReset&&clearTimeout(this._openReset),this._endedHide&&clearTimeout(this._endedHide)}_phaseOf(e){let r=this.hass?.states[e.call_state]?.state;return Qe(r)}get _active(){let e=this._doorbells.find(r=>le.has(this._phaseOf(r))&&!this._errDismissed.has(r.call_state));if(e)return e;if(this._endedEntity)return this._doorbells.find(r=>r.call_state===this._endedEntity)}get _phase(){let e=this._active;if(!e)return"idle";let r=this._phaseOf(e);return le.has(r)?r:e.call_state===this._endedEntity?"ended":"idle"}get _intercomName(){let e=this._active;if(e?.name)return e.name;let i=(e?this.hass?.states[e.call_state]?.attributes:void 0)?.intercom_name;return(typeof i=="string"?i.replace(/\s+/g," ").trim():"")||this._config.name||_(this._lang).nameFallback}get _address(){return this._active?.address??this._config.address??""}get _lang(){return ne(this.hass)}get _startedAtMs(){let e=this._active,r=e?this.hass?.states[e.call_state]?.attributes?.started_at:void 0;if(typeof r!="string")return;let i=Date.parse(r);return Number.isNaN(i)?void 0:i}willUpdate(e){if(!e.has("hass"))return;for(let n of this._doorbells){let a=this._phaseOf(n),l=this._prevPhases.get(n.call_state);this._prevPhases.set(n.call_state,a),this._errDismissed.has(n.call_state)&&a!=="error"&&this._errDismissed.delete(n.call_state),a==="ended"&&l!==void 0&&le.has(l)&&l!=="error"&&this._enterEnded(n),this._endedEntity===n.call_state&&le.has(a)&&this._clearEnded()}let r=this._active,i=r?`${r.call_state}|${this._phase}`:"idle";i!==this._prevKey&&(this._onPhase(this._phase,r),this._prevKey=i)}_enterEnded(e){this._endedDuration=this._durationOf(e),this._endedEntity=e.call_state,this._endedHide&&clearTimeout(this._endedHide),this._endedHide=window.setTimeout(()=>this._clearEnded(),It)}_durationOf(e){let r=this.hass?.states[e.call_state]?.attributes?.started_at;if(typeof r!="string")return"";let i=Date.parse(r);return Number.isNaN(i)?"":this._mmss(Math.max(0,Math.floor((Date.now()-i)/1e3)))}_onPhase(e,r){e==="active"?this._enterActive():e==="ringing"?(this._ringingSince=Date.now(),this._startTick()):this._exitActive(),e==="error"&&r&&this._scheduleErrDismiss(r.call_state),(e==="idle"||e==="ringing")&&(this._openStatus="idle")}async _enterActive(){if(this._muted=!1,this._audioBlocked=this._detectAudioBlocked(),this._startTick(),this._config.mic===!1||(this._micPerm=await this._mic.queryPermission(),this._phase!=="active"))return;this._config.mic_autostart!==!1&&st(this._micPerm,this._mic.secure,this._mic.hasGrantedBefore())&&(await this._mic.start(),this._micPerm=await this._mic.queryPermission())}_detectAudioBlocked(){let e=navigator.userActivation;return e?!e.hasBeenActive:!1}_exitActive(){this._mic.stop(),this._stopTick(),this._audioBlocked=!1}_startTick(){this._stopTick(),this._now=Date.now(),this._tick=window.setInterval(()=>{this._now=Date.now()},1e3)}_stopTick(){this._tick&&(clearInterval(this._tick),this._tick=void 0)}_scheduleErrDismiss(e){this._errHide&&clearTimeout(this._errHide),this._errHide=window.setTimeout(()=>{this._errDismissed=new Set(this._errDismissed).add(e),this.requestUpdate()},Bt)}_timerText(){let e=this._startedAtMs;if(e===void 0)return"";let r=Math.max(0,Math.floor((this._now-e)/1e3));return this._mmss(r)}_mmss(e){let r=String(Math.floor(e/60)).padStart(2,"0"),i=String(e%60).padStart(2,"0");return`${r}:${i}`}_answerWindow(){if(!this._ringingSince)return{text:"",fraction:0};let e=Math.max(0,ct-(this._now-this._ringingSince)),r=Math.ceil(e/1e3);return{text:`${Math.floor(r/60)}:${String(r%60).padStart(2,"0")}`,fraction:e/ct}}_stageState(e,r,i){if(i==="ended")return"ended";if(e.isError)return"connection_lost";let n=r?this.hass?.states[r]:void 0;return!n||n.state==="unavailable"?"camera_off":"live"}get _micBanner(){return this._config.mic===!1||this._phase!=="active"||this._micActive?"none":nt(this._mic.secure,this._micPerm,this._mic.hasGrantedBefore())}get _micBlocked(){return!this._mic.secure||this._micPerm==="denied"}render(){let e=this._active;if(!e)return this._renderIdle();let r=this._phase,i=et(r),n=tt(i.video,{camera:this._config.camera,doorbell_camera:e.doorbell_camera});if(this._config.layout==="compact")return this._renderCompact(e,r,i,n);let a=this._stageState(i,n,r);return c`
      <ha-card class="phase-${r}">
        <div class="content">
          ${this._renderHeader()}
          ${this._renderStatus(i,r)}
          <div class="stage">
            <mdr-call-stage
              .hass=${this.hass}
              .uiLang=${this._lang}
              .entity=${n}
              .muted=${this._muted||this._audioBlocked}
              .live=${a==="live"}
              .soundOff=${r==="active"&&this._muted&&!this._audioBlocked}
              .stageState=${a}
              .audioBlocked=${this._audioBlocked}
              @unmute=${this._unmute}
            ></mdr-call-stage>
          </div>
          <div class="controls">
            ${(()=>{let l=this._micBanner;return l!=="none"?this._renderMicBanner(l):p})()}
            <div class="open-area">
              ${i.showOpen?this._renderOpen():p}
            </div>
            ${this._renderActions(i)}
          </div>
        </div>
      </ha-card>
    `}_renderHeader(){let e=this._address;return c`
      <header>
        <div class="hgroup">
          <span class="name" title=${this._intercomName}>${this._intercomName}</span>
          ${e?c`<span class="addr">${e}</span>`:p}
        </div>
        <button class="close" @click=${this._dismiss} aria-label=${_(this._lang).minimize}>
          <mdr-icon name="x"></mdr-icon>
        </button>
      </header>
    `}_renderStatus(e,r){let i=e.showTimer&&this._config.timer!=="off",n=e.showAnswerWindow?this._answerWindow():null;return c`
      <div class="statusrow">
        <div class="strow">
          <span class="badge" style="--badge:${ke(r)}">
            <span class="dot" aria-hidden="true"></span>
            <span>${_(this._lang).status[r]??""}</span>
          </span>
          ${n?c`<span class="countdown"><mdr-icon name="timer"></mdr-icon>${n.text}</span>`:i?c`<span class="timer">${this._timerText()}</span>`:r==="ended"&&this._endedDuration?c`<span class="timer ended-dur">${this._endedDuration}</span>`:p}
        </div>
        ${n?c`<div class="window"><div class="fill" style="width:${n.fraction*100}%"></div></div>`:p}
      </div>
    `}_doorbellNames(){return this._doorbells.map(e=>{let r=this.hass?.states[e.call_state]?.attributes?.intercom_name;return e.name??(typeof r=="string"?r:"")}).filter(Boolean)}_renderIdle(){let e=this._doorbellNames();return c`
      <ha-card class="idle">
        <div class="idle-box" role="status">
          <div class="idle-ico"><mdr-icon name="door-closed"></mdr-icon></div>
          <div class="idle-title">${this._config.idle_text??_(this._lang).idle.title}</div>
          <div class="idle-sub">${_(this._lang).idle.sub}</div>
          ${e.length?c`<div class="idle-chips">
                ${e.map(r=>c`<span class="chip"><mdr-icon name="door-open"></mdr-icon>${r}</span>`)}
              </div>`:p}
        </div>
      </ha-card>
    `}_renderCompact(e,r,i,n){let a=this._stageState(i,n,r);return c`
      <ha-card class="compact phase-${r}">
        <div class="cx-thumb">
          ${n?c`<mdr-call-video .hass=${this.hass} .entity=${n} .muted=${!0}></mdr-call-video>`:p}
          ${a==="live"?c`<span class="cx-live">LIVE</span>`:p}
        </div>
        <div class="cx-info">
          <span class="cx-name" title=${this._intercomName}>${this._intercomName}</span>
          <span class="cx-status" style="--badge:${ke(r)}">
            <span class="cx-dot" aria-hidden="true"></span>
            <span>${this._compactStatus(r)}</span>
          </span>
        </div>
        <div class="cx-btns">
          ${i.showOpen&&e.lock?this._quickBtn("key-round",_(this._lang).open.slide,this._open,"q-open"):p}
          ${i.actions.map(l=>this._quickAction(l))}
        </div>
      </ha-card>
    `}_quickAction(e){let r=_(this._lang).action;switch(e){case"accept":return this._quickBtn("phone",r.accept,this._answer,"q-accept");case"reject":case"cancel":case"hangup":return this._quickBtn("phone-off",r.hangup,this._hangup,"q-reject");case"close":return this._quickBtn("x",r.close,this._clearEnded,"");default:return p}}_quickBtn(e,r,i,n){return c`
      <button class="q-btn ${n}" @click=${i} aria-label=${r}>
        <mdr-icon name=${e}></mdr-icon>
      </button>
    `}_compactStatus(e){let r=_(this._lang).compact;return e==="ringing"?`${r.call} \xB7 ${this._answerWindow().text}`:e==="active"?`${r.talk} \xB7 ${this._timerText()}`:e==="connecting"?r.connecting:e==="ended"?this._endedDuration?`${r.ended} \xB7 ${this._endedDuration}`:r.ended:e==="error"?r.error:""}_renderMicBanner(e){let r=_(this._lang).micBanner[e];return c`
      <div class="mic-banner" role="alert">
        <mdr-icon name="mic-off"></mdr-icon>
        <div class="mb-text">
          <span class="mb-title">${r.title}</span>
          <span class="mb-sub">${r.sub}</span>
        </div>
        ${r.cta?c`<button class="mb-btn" @click=${this._toggleMic}>${r.cta}</button>`:p}
      </div>
    `}_renderOpen(){return c`
      <mdr-open-control
        .mode=${this._openAction}
        .status=${this._openStatus}
        .uiLang=${this._lang}
        ?disabled=${!this._active?.lock}
        @open=${this._open}
      ></mdr-open-control>
    `}_circle(e,r,i,n=""){return c`
      <button class="circle ${n}" @click=${i} aria-label=${r}>
        <span class="ic"><mdr-icon name=${e}></mdr-icon></span>
        <small>${r}</small>
      </button>
    `}_renderActions(e){return c`<div class="actions">${e.actions.map(r=>this._renderAction(r))}</div>`}_renderAction(e){let r=_(this._lang).action;switch(e){case"accept":return this._circle("phone",r.accept,this._answer,"accept");case"reject":return this._circle("phone-off",r.reject,this._hangup,"reject");case"cancel":return this._circle("phone-off",r.cancel,this._hangup,"reject");case"connecting":return this._spinnerBtn(r.connecting);case"mic":return this._config.mic===!1?p:this._renderMic();case"sound":return this._audioBlocked?this._circle("volume-x",r.soundOff,this._unmute,"warn"):this._circle(this._muted?"volume-x":"volume-2",r.sound,this._toggleMute);case"hangup":return this._circle("phone-off",r.hangup,this._hangup,"reject");case"retry":return this._circle("refresh-cw",r.retry,this._retry,"retry");case"close":return this._circle("x",r.close,this._clearEnded);default:return p}}_spinnerBtn(e){return c`
      <div class="circle spinner-btn" role="status" aria-label=${e} aria-busy="true">
        <span class="ic"><mdr-icon class="spin" name="loader-circle"></mdr-icon></span>
        <small>${e}</small>
      </div>
    `}_renderMic(){let e=_(this._lang).action;if(this._micBlocked)return this._circle("mic-off",e.micNoAccess,this._toggleMic,"mic-blocked");let r=this._micActive?"mic":"mic-off",i=this._micActive?e.micOff:e.micOn;return c`<button class="circle" @click=${this._toggleMic} aria-label=${i}>
      <span class="ic"><mdr-icon name=${r}></mdr-icon></span><small>${e.mic}</small>
    </button>`}};x.styles=[M,w`
      :host {
        display: block;
        height: 100%;
        /* адаптив по собственной ширине карточки (телефон / планшет / десктоп / панель) */
        container-type: inline-size;
      }
      ha-card {
        height: 100%;
        box-sizing: border-box;
        background: var(--mdr-card);
        border-radius: var(--mdr-r-card);
      }
      .content {
        display: flex;
        flex-direction: column;
        gap: 20px;
        /* заполняем высоту карточки; вертикальный экран → верт. отступы вдвое больше
           горизонтальных (16), с учётом safe-area панели/телефона */
        min-height: 100%;
        padding: max(32px, env(safe-area-inset-top)) 16px max(32px, env(safe-area-inset-bottom));
        box-sizing: border-box;
      }
      /* Адаптивный масштаб контента: телефон = 1, на большом экране крупнее
         (настенная панель/десктоп — «читаемо с ~1м», UX §10). Наследуется в
         дочерние компоненты (open-control) через --mdr-scale. */
      .content,
      ha-card.idle {
        --mdr-scale: 1;
      }
      @container (min-width: 700px) {
        .content,
        ha-card.idle {
          --mdr-scale: 1.35;
        }
      }
      @container (min-width: 1100px) {
        .content,
        ha-card.idle {
          --mdr-scale: 1.7;
        }
      }
      @container (min-width: 1600px) {
        .content,
        ha-card.idle {
          --mdr-scale: 2;
        }
      }
      /* шапка/статус/видео — сверху, фиксированной высоты */
      header,
      .statusrow,
      .stage {
        flex: none;
      }
      /* зона контролов заполняет остаток: слайдер по центру, кнопки — по нижней кромке */
      .controls {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px;
      }
      .controls .open-area {
        flex: 1;
        align-items: center;
      }
      .controls .actions {
        margin-top: auto;
      }
      /* ---- широкий контейнер (планшет / настенная панель / десктоп): 2 колонки.
         Порог 760px: видео + контролы РЯДОМ вертикально компактнее вертикального
         стека, поэтому на невысоких экранах ничего не переполняется (у стека
         video 16:9 + баннер + слайдер + кнопки не влезают по высоте). */
      @container (min-width: 760px) {
        .content {
          display: grid;
          /* Узкая колонка контролов фикс. ширины → видео (1fr) получает
             максимум ширины, а значит и высоты (оно всегда 16:9). Кнопки/
             слайдер — базового размера (.controls сбрасывает --mdr-scale в 1):
             на десктопе (мышь, близко) укрупнённые touch-таргеты не нужны. */
          grid-template-columns: 1fr 320px;
          grid-template-areas:
            "header header"
            "status status"
            "stage controls";
          column-gap: 28px;
          row-gap: 20px;
          align-items: start;
          /* grid default align-content = stretch → строки растягивались (дыры);
             start = контент сверху, строка stage/controls по высоте видео */
          align-content: start;
          padding: 24px;
        }
        header {
          grid-area: header;
        }
        .statusrow {
          grid-area: status;
        }
        .stage {
          grid-area: stage;
          align-self: start;
        }
        /* Колонка контролов = высоте видео (align-self: stretch). Flex-поток
           (из базового .controls): баннер сверху, слайдер по центру свободного
           места, кнопки по нижней кромке — без наложения при любой высоте видео
           (в т.ч. на узком 760–900, где видео невысокое). */
        .controls {
          grid-area: controls;
          align-self: stretch;
          /* Базовый размер контролов на широком экране: --mdr-scale укрупняет
             текст/оверлеи для читаемости, но кнопки/слайдер от него раздувались
             до ~2× («как для слепых» на десктопе). Здесь сбрасываем в 1. */
          --mdr-scale: 1;
        }
      }
      /* ≥900px: видео уже выше стека контролов → абсолютное позиционирование,
         слайдер строго по ЦЕНТРУ видео, кнопки по нижней кромке, баннер сверху.
         На 760–900 остаётся flex-поток (выше) — иначе слайдер/кнопки налезали
         бы друг на друга на невысоком видео. */
      @container (min-width: 900px) {
        .controls {
          position: relative;
          display: block;
        }
        .controls .mic-banner {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
        }
        .controls .open-area {
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(-50%);
        }
        .controls .actions {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
        }
      }
      /* ---- шапка: имя + адрес + свернуть ---- */
      header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
      }
      .hgroup {
        display: flex;
        flex-direction: column;
        gap: 3px;
        min-width: 0;
      }
      .name {
        font-size: calc(22px * var(--mdr-scale, 1));
        font-weight: 700;
        line-height: 1.15;
        color: var(--mdr-text);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .addr {
        font-size: calc(13px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .close {
        flex: none;
        width: calc(44px * var(--mdr-scale, 1));
        height: calc(44px * var(--mdr-scale, 1));
        border: none;
        border-radius: var(--mdr-r-full);
        background: var(--mdr-elevated);
        color: var(--mdr-text-2);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
      }
      .close mdr-icon {
        --mdr-icon-size: calc(20px * var(--mdr-scale, 1));
      }
      /* ---- статус-строка: бейдж + таймер/countdown + окно ответа ---- */
      .statusrow {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .strow {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
      }
      .badge {
        display: inline-flex;
        align-items: center;
        gap: calc(7px * var(--mdr-scale, 1));
        padding: calc(5px * var(--mdr-scale, 1)) calc(12px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        font-size: calc(13px * var(--mdr-scale, 1));
        font-weight: 600;
        color: var(--badge, var(--mdr-text-2));
        background: color-mix(in srgb, var(--badge, var(--mdr-text-2)) 18%, transparent);
      }
      .badge .dot {
        width: calc(8px * var(--mdr-scale, 1));
        height: calc(8px * var(--mdr-scale, 1));
        border-radius: 50%;
        background: var(--badge, var(--mdr-text-2));
      }
      .countdown {
        display: inline-flex;
        align-items: center;
        gap: calc(6px * var(--mdr-scale, 1));
        font-size: calc(15px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
      }
      .countdown mdr-icon {
        --mdr-icon-size: calc(15px * var(--mdr-scale, 1));
      }
      .timer {
        font-family: var(--mdr-mono);
        font-size: calc(17px * var(--mdr-scale, 1));
        font-weight: 600;
        color: var(--mdr-text);
        font-variant-numeric: tabular-nums;
      }
      .timer.ended-dur {
        color: var(--mdr-text-3);
        font-weight: 500;
      }
      .window {
        width: 100%;
        height: 4px;
        border-radius: var(--mdr-r-full);
        background: var(--mdr-elevated);
        overflow: hidden;
      }
      .window .fill {
        height: 100%;
        border-radius: var(--mdr-r-full);
        background: var(--mdr-warning);
        transition: width 1s linear;
      }
      /* ---- баннер «нет доступа к микрофону» ---- */
      .mic-banner {
        display: flex;
        align-items: center;
        gap: calc(12px * var(--mdr-scale, 1));
        padding: calc(12px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-md);
        background: var(--mdr-warning-bg);
      }
      .mic-banner > mdr-icon {
        --mdr-icon-size: calc(20px * var(--mdr-scale, 1));
        color: var(--mdr-warning);
      }
      .mb-text {
        display: flex;
        flex-direction: column;
        gap: 2px;
        flex: 1;
        min-width: 0;
      }
      .mb-title {
        font-size: calc(13px * var(--mdr-scale, 1));
        font-weight: 600;
        color: var(--mdr-warning);
      }
      .mb-sub {
        font-size: calc(12px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
      }
      .mb-btn {
        flex: none;
        border: 1px solid var(--mdr-warning);
        background: transparent;
        color: var(--mdr-warning);
        font: inherit;
        font-size: calc(13px * var(--mdr-scale, 1));
        font-weight: 600;
        border-radius: var(--mdr-r-full);
        padding: calc(6px * var(--mdr-scale, 1)) calc(14px * var(--mdr-scale, 1));
        cursor: pointer;
      }
      /* ---- видео-стейдж ---- */
      .stage {
        position: relative;
        width: 100%;
        aspect-ratio: 16 / 9;
        border-radius: var(--mdr-r-md);
        overflow: hidden;
        background: var(--mdr-elevated);
      }
      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .spin {
          animation: none;
        }
      }
      /* ---- зона «Открыть» ---- */
      .open-area {
        display: flex;
        justify-content: center;
      }
      .open-area mdr-open-control {
        width: 100%;
      }
      /* ---- ряд действий: круги top-align (как в макете), gap 28 ---- */
      .actions {
        display: flex;
        gap: calc(28px * var(--mdr-scale, 1));
        justify-content: center;
        align-items: flex-start;
        flex-wrap: wrap;
      }
      .circle {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: calc(8px * var(--mdr-scale, 1));
        border: none;
        background: none;
        cursor: pointer;
        color: var(--mdr-text);
        font: inherit;
        padding: 0;
      }
      .circle .ic {
        width: calc(68px * var(--mdr-scale, 1));
        height: calc(68px * var(--mdr-scale, 1));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--mdr-elevated);
        color: var(--mdr-text);
      }
      .circle .ic mdr-icon {
        --mdr-icon-size: calc(28px * var(--mdr-scale, 1));
      }
      .circle small {
        font-size: calc(12px * var(--mdr-scale, 1));
        font-weight: 500;
        color: var(--mdr-text-2);
      }
      .circle[disabled] {
        cursor: not-allowed;
        opacity: 0.5;
      }
      /* Все кнопки ряда — единый стиль: круг 68, иконка 28, подпись fs12/fw500/text-2.
         Акцент действия — только ЦВЕТОМ круга (см. call-card-ux-production.md §6/§9). */
      .circle.accept .ic {
        background: var(--mdr-success);
        color: var(--mdr-on-fill);
      }
      .circle.reject .ic {
        background: var(--mdr-error);
        color: var(--mdr-on-fill);
      }
      .circle.retry .ic {
        background: var(--mdr-primary);
        color: var(--mdr-on-fill);
      }
      /* audio_blocked: «Звук выкл.» — warning-иконка на elevated */
      .circle.warn .ic {
        color: var(--mdr-warning);
      }
      .circle.warn small {
        color: var(--mdr-warning);
      }
      /* микрофон недоступен: красный индикатор «Нет доступа» (iUNo1) */
      .circle.mic-blocked .ic {
        background: var(--mdr-error-bg);
        color: var(--mdr-error);
      }
      .circle.mic-blocked small {
        color: var(--mdr-error);
      }
      /* «Соединяем…» — неинтерактивно, приглушённый крутящийся loader */
      .spinner-btn {
        cursor: default;
      }
      .spinner-btn small {
        color: var(--mdr-text-3);
      }
      .spinner-btn .ic mdr-icon.spin {
        color: var(--mdr-text-2);
        animation: spin 0.9s linear infinite;
      }
      /* ---- idle-заглушка (узел aSs3Z) ---- */
      ha-card.idle {
        height: 100%;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 18px;
      }
      .idle-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: calc(18px * var(--mdr-scale, 1));
        text-align: center;
      }
      .idle-ico {
        width: calc(76px * var(--mdr-scale, 1));
        height: calc(76px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: var(--mdr-elevated);
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .idle-ico mdr-icon {
        --mdr-icon-size: calc(36px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
      }
      .idle-title {
        font-size: calc(22px * var(--mdr-scale, 1));
        font-weight: 700;
        color: var(--mdr-text);
      }
      .idle-sub {
        font-size: calc(15px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
        max-width: 40ch;
      }
      .idle-chips {
        display: flex;
        flex-wrap: wrap;
        gap: calc(10px * var(--mdr-scale, 1));
        justify-content: center;
        padding-top: calc(6px * var(--mdr-scale, 1));
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: calc(7px * var(--mdr-scale, 1));
        padding: calc(9px * var(--mdr-scale, 1)) calc(16px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: var(--mdr-elevated);
        color: var(--mdr-text-2);
        font-size: calc(14px * var(--mdr-scale, 1));
        font-weight: 500;
      }
      .chip mdr-icon {
        --mdr-icon-size: calc(16px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
      }
      /* ---- компактная строка (layout: compact) — узел aSs3Z ---- */
      ha-card.compact {
        height: auto;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        box-sizing: border-box;
      }
      .cx-thumb {
        position: relative;
        width: 80px;
        height: 60px;
        flex: none;
        border-radius: 10px;
        overflow: hidden;
        background: #20262b;
      }
      .cx-thumb mdr-call-video {
        position: absolute;
        inset: 0;
      }
      .cx-live {
        position: absolute;
        top: 6px;
        left: 6px;
        padding: 2px 6px;
        border-radius: var(--mdr-r-full);
        background: rgba(211, 47, 47, 0.88);
        color: #fff;
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 0.04em;
      }
      .cx-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 5px;
      }
      .cx-name {
        font-size: 15px;
        font-weight: 700;
        color: var(--mdr-text);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .cx-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 500;
        color: var(--badge, var(--mdr-text-2));
      }
      .cx-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--badge, var(--mdr-text-2));
        flex: none;
      }
      .cx-btns {
        display: flex;
        gap: 8px;
        flex: none;
      }
      .q-btn {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--mdr-elevated);
        color: var(--mdr-text);
      }
      .q-btn mdr-icon {
        --mdr-icon-size: 20px;
      }
      .q-btn.q-open {
        background: var(--mdr-primary);
        color: var(--mdr-on-fill);
      }
      .q-btn.q-accept {
        background: var(--mdr-success);
        color: var(--mdr-on-fill);
      }
      .q-btn.q-reject {
        background: var(--mdr-error);
        color: var(--mdr-on-fill);
      }
    `],d([m({attribute:!1})],x.prototype,"hass",2),d([f()],x.prototype,"_config",2),d([f()],x.prototype,"_muted",2),d([f()],x.prototype,"_audioBlocked",2),d([f()],x.prototype,"_micActive",2),d([f()],x.prototype,"_micPerm",2),d([f()],x.prototype,"_openStatus",2),d([f()],x.prototype,"_now",2),d([f()],x.prototype,"_ringingSince",2),d([f()],x.prototype,"_errDismissed",2),d([f()],x.prototype,"_endedEntity",2),d([f()],x.prototype,"_endedDuration",2),x=d([k("mdr-intercom-call-card")],x);window.customCards=window.customCards||[];window.customCards.push({type:"mdr-intercom-call-card",name:"\u0423\u043C\u043D\u044B\u0439 \u0414\u043E\u043C.\u0440\u0443 \u2014 \u0412\u044B\u0437\u043E\u0432 \u0434\u043E\u043C\u043E\u0444\u043E\u043D\u0430",description:"Doorbell incoming call & talk: video+audio, open door, accept/hang up, mic \u2014 one card for all intercoms. \u0412\u0445\u043E\u0434\u044F\u0449\u0438\u0439 \u0432\u044B\u0437\u043E\u0432 \u0438 \u0440\u0430\u0437\u0433\u043E\u0432\u043E\u0440 \u0441 \u0434\u043E\u043C\u043E\u0444\u043E\u043D\u043E\u043C: \u0432\u0438\u0434\u0435\u043E+\u0437\u0432\u0443\u043A, \u043E\u0442\u043A\u0440\u044B\u0442\u044C \u0434\u0432\u0435\u0440\u044C, \u043F\u0440\u0438\u043D\u044F\u0442\u044C/\u0437\u0430\u0432\u0435\u0440\u0448\u0438\u0442\u044C, \u043C\u0438\u043A\u0440\u043E\u0444\u043E\u043D.",preview:!1});export{x as EgIntercomCallCard};
